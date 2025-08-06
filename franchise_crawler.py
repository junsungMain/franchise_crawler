import requests
import pandas as pd
from typing import Dict, Any, List
import time
import html

class FranchiseCrawler:
    def __init__(self):
        self.base_url = "https://www.k-franchise.or.kr"
        self.list_endpoint = "/brand/bprl/list/read"
        self.detail_endpoint = "/brand/bprl/readFrcsor"
        self.session = requests.Session()
        self.category_code = "TP00000048"  # 기본값: 카페 & 디저트
        self.log_callback = None  # 로그 콜백 함수
        self.stop_flag = False  # 중지 플래그
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def stop(self):
        """크롤링 중지"""
        self.stop_flag = True
        self.log("중지 요청됨...")
    
    def reset_stop_flag(self):
        """중지 플래그 초기화"""
        self.stop_flag = False
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def decode_html_entities(self, text: str) -> str:
        if not text:
            return text
        return html.unescape(str(text))
    
    def get_franchise_list(self, page_num: int = 1) -> Dict[str, Any]:
        payload = {
            "kfaTpindLv1Cd": self.category_code,
            "kfaTpindLv2Cd": "",
            "pageNum": page_num,
            "pagePerRows": 20,
            "pageCount": 5,
            "sortGubun": "BASIC",
            "minCost": "",
            "maxCost": "",
            "minArea": "",
            "maxArea": ""
        }
        
        headers = self.session.headers.copy()
        headers['Content-Type'] = 'application/json'
        
        try:
            response = self.session.post(
                f"{self.base_url}{self.list_endpoint}",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"목록 API 오류: {e}")
            return {"error": str(e)}
    
    def get_franchise_detail(self, brnd_cd: str, frcsor_no: str) -> Dict[str, Any]:
        data = {
            "frcsorNo": frcsor_no,
            "brndCd": brnd_cd
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}{self.detail_endpoint}",
                data=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log(f"상세 API 오류: {e}")
            return {"error": str(e)}
    
    def get_all_franchises(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        all_franchises = []
        page = 1
        
        # 중지 플래그 초기화
        self.reset_stop_flag()
        
        while page <= max_pages:
            # 중지 플래그 확인
            if self.stop_flag:
                self.log("크롤링이 중지되었습니다.")
                break
                
            self.log(f"페이지 {page} 수집 중...")
            
            response = self.get_franchise_list(page_num=page)
            
            if "error" in response:
                self.log(f"페이지 {page} 오류: {response['error']}")
                break
            
            if response.get("retCode") == "CM0000" or response.get("retMsg") == "SUCCESS":
                franchises = response.get("data", {}).get("list", [])
                if not franchises:
                    self.log(f"페이지 {page}에서 더 이상 데이터가 없습니다.")
                    break
                
                for franchise in franchises:
                    # 중지 플래그 확인
                    if self.stop_flag:
                        self.log("크롤링이 중지되었습니다.")
                        return all_franchises
                    
                    brnd_cd = franchise.get('brndCd')
                    frcsor_no = franchise.get('frcsorNo')
                    
                    if brnd_cd and frcsor_no:
                        detail_response = self.get_franchise_detail(brnd_cd, frcsor_no)
                        
                        if detail_response.get("retCode") == "CM0000" or detail_response.get("retMsg") == "SUCCESS":
                            detail_data = detail_response.get("data", {}).get("frcsor", {}) or {}
                            
                            # 전화번호 형식 개선
                            telno = franchise.get('telno', '')
                            if telno and isinstance(telno, (int, float)):
                                telno = str(int(telno))
                            
                            combined_data = {
                                '상호': self.decode_html_entities(franchise.get('bzname', '')),
                                '영업표지': self.decode_html_entities(franchise.get('brndNm', '')),
                                '대표자': self.decode_html_entities(detail_data.get('reprNm', '')),
                                '업종': self.decode_html_entities(franchise.get('tpindNm', '')),
                                '대표번호': telno,
                                '대표팩스번호': franchise.get('faxno', ''),
                                '주소': self.decode_html_entities(f"{detail_data.get('adr', '')} {detail_data.get('dtlAdr', '')}".strip()),
                                '사업자등록번호': franchise.get('brno', '')
                            }
                            
                            all_franchises.append(combined_data)
                        else:
                            self.log(f"    상세 정보 수집 실패: {detail_response.get('retMsg', '알 수 없는 오류')}")
                    else:
                        self.log(f"    brndCd 또는 frcsorNo가 없습니다: {self.decode_html_entities(franchise.get('bzname', 'N/A'))}")
                
                self.log(f"페이지 {page}에서 {len(franchises)}개 수집")
                page += 1
            else:
                self.log(f"페이지 {page} 응답 오류: {response.get('retMsg', '알 수 없는 오류')}")
                break
        
        return all_franchises
    
    def save_to_excel(self, franchises: List[Dict[str, Any]], filename: str = "franchise_data.xlsx"):
        if not franchises:
            self.log("저장할 데이터가 없습니다.")
            return
        
        df = pd.DataFrame(franchises)
        df.to_excel(filename, index=False, engine='openpyxl')
        self.log(f"데이터가 {filename} 파일에 저장되었습니다.")
        self.log(f"총 {len(franchises)}개의 프랜차이즈 데이터가 저장되었습니다.")


def main():
    crawler = FranchiseCrawler()
    
    print("프랜차이즈 데이터 수집을 시작합니다...")
    all_franchises = crawler.get_all_franchises(max_pages=10)
    
    if all_franchises:
        crawler.save_to_excel(all_franchises, "franchise_data.xlsx")
    else:
        print("수집된 데이터가 없습니다.")


if __name__ == "__main__":
    main()
