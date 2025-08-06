import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from franchise_crawler import FranchiseCrawler
import os

class FranchiseCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("프랜차이즈 데이터 수집")
        self.root.geometry("700x600")
        
        # 업종 정보
        self.categories = {
            "카페 & 디저트": "TP00000048",
            "음식점 & 주점": "TP00000052", 
            "치킨 & 피자": "TP00000059",
            "분식 & 패스트푸드": "TP00000062",
            "판매업": "TP00000065",
            "서비스업": "TP00000071"
        }
        
        self.crawler = FranchiseCrawler()
        self.setup_ui()
        
    def setup_ui(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="프랜차이즈 데이터 수집", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 업종 선택 프레임
        category_frame = ttk.LabelFrame(main_frame, text="", padding="10")
        category_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 업종 선택 제목 (굵게)
        category_title = ttk.Label(category_frame, text="업종 선택", font=("Arial", 12, "bold"))
        category_title.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 업종 버튼들
        self.category_var = tk.StringVar()
        row = 1
        col = 0
        for category_name in self.categories.keys():
            btn = ttk.Radiobutton(
                category_frame, 
                text=category_name, 
                variable=self.category_var, 
                value=category_name
            )
            btn.grid(row=row, column=col, sticky=tk.W, padx=(0, 20), pady=5)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # 기본값 설정
        self.category_var.set("카페 & 디저트")
        
        # 설정 프레임
        settings_frame = ttk.LabelFrame(main_frame, text="", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # 설정 제목 (굵게)
        settings_title = ttk.Label(settings_frame, text="설정", font=("Arial", 12, "bold"))
        settings_title.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 페이지 수 설정
        ttk.Label(settings_frame, text="수집할 페이지 수:").grid(row=1, column=0, sticky=tk.W)
        self.page_var = tk.StringVar(value="10")
        page_spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, textvariable=self.page_var, width=10)
        page_spinbox.grid(row=1, column=1, padx=(10, 0))
        
        # 파일명 설정
        ttk.Label(settings_frame, text="저장할 파일명:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.filename_var = tk.StringVar(value="franchise_data")
        filename_entry = ttk.Entry(settings_frame, textvariable=self.filename_var, width=30)
        filename_entry.grid(row=2, column=1, padx=(10, 0), pady=(10, 0))
        
        # 진행 상황 프레임
        progress_frame = ttk.LabelFrame(main_frame, text="", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # 진행 상황 제목 (굵게)
        progress_title = ttk.Label(progress_frame, text="진행 상황", font=("Arial", 12, "bold"))
        progress_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 진행바
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 로그 텍스트
        self.log_text = tk.Text(progress_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # 시작 버튼
        self.start_btn = ttk.Button(button_frame, text="수집 시작", command=self.start_crawling)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        # 중지 버튼
        self.stop_btn = ttk.Button(button_frame, text="중지", command=self.stop_crawling, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        # 닫기 버튼
        close_btn = ttk.Button(button_frame, text="닫기", command=self.close_app)
        close_btn.grid(row=0, column=2)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)  # 진행 상황 프레임이 확장되도록
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(2, weight=1)  # 로그 텍스트가 확장되도록
        
        self.is_running = False
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_crawling(self):
        if self.is_running:
            return
            
        category_name = self.category_var.get()
        if not category_name:
            messagebox.showerror("오류", "업종을 선택해주세요.")
            return
            
        try:
            max_pages = int(self.page_var.get())
        except ValueError:
            messagebox.showerror("오류", "올바른 페이지 수를 입력해주세요.")
            return
            
        filename = self.filename_var.get()
        if not filename:
            messagebox.showerror("오류", "파일명을 입력해주세요.")
            return
            
        # .xlsx 확장자 추가
        if not filename.endswith('.xlsx'):
            filename = filename + '.xlsx'
            
        # result 폴더 경로로 고정
        result_dir = os.path.join(os.getcwd(), 'result')
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        filename = os.path.join(result_dir, filename)
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        
        # 로그 초기화
        self.log_text.delete(1.0, tk.END)
        self.log(f"업종: {category_name}")
        self.log(f"페이지 수: {max_pages}")
        self.log(f"파일명: {filename}")
        self.log("-" * 50)
        
        # 별도 스레드에서 크롤링 실행
        thread = threading.Thread(
            target=self.crawl_data,
            args=(category_name, max_pages, filename)
        )
        thread.daemon = True
        thread.start()
    
    def crawl_data(self, category_name, max_pages, filename):
        try:
            # 크롤러의 카테고리 코드 설정
            category_code = self.categories[category_name]
            self.crawler.category_code = category_code
            
            # 로그 콜백 함수 설정
            def log_callback(message):
                self.root.after(0, self.log, message)
            
            self.crawler.log_callback = log_callback
            
            # 데이터 수집
            all_franchises = self.crawler.get_all_franchises(max_pages=max_pages)
            
            if all_franchises:
                # 엑셀 저장
                self.crawler.save_to_excel(all_franchises, filename)
                self.root.after(0, self.log, f"✅ 완료! {len(all_franchises)}개 데이터 수집")
                self.root.after(0, self.crawling_finished, True)
            else:
                self.root.after(0, self.log, "❌ 수집된 데이터가 없습니다.")
                self.root.after(0, self.crawling_finished, False)
                
        except Exception as e:
            self.root.after(0, self.log, f"❌ 오류 발생: {str(e)}")
            self.root.after(0, self.crawling_finished, False)
    
    def crawling_finished(self, success):
        self.is_running = False
        self.progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        if success:
            messagebox.showinfo("완료", "데이터 수집이 완료되었습니다!")
    
    def stop_crawling(self):
        self.is_running = False
        self.crawler.stop()  # 크롤러 중지 메서드 호출
        self.log("⏹️ 사용자가 중지했습니다.")
        self.progress.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def close_app(self):
        """프로그램 종료"""
        if self.is_running:
            # 크롤링 중이면 중지 확인
            if messagebox.askyesno("확인", "크롤링이 진행 중입니다. 정말 종료하시겠습니까?"):
                self.crawler.stop()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = FranchiseCrawlerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 