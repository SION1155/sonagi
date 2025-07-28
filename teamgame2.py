import pygame
import random
import sys
import tkinter as tk
from threading import Thread
import queue
import time

# ====================
# 한자 ↔ 훈음 & 뜻 매핑
# ====================
hanja_dict = {
    "仁": "인", "義": "의", "禮": "예",
    "正名": "정명", "德治": "덕치", "無欲": "무욕",
    "謙虛": "겸허", "不爭": "부쟁", "無爲之治": "무위지치",
    "反者道之動": "반자도지동", "弱者道之用": "약자도지용",
    "慈悲": "자비", "輪廻": "윤회", "解脫": "해탈",
    "中道": "중도", "一切唯心造": "일체유심조",
    "克己復禮": "극기복례", "克己": "극기", "天下": "천하",
    "兼愛": "겸애", "仁義": "인의",
    "天長地久": "천장지구", "國": "국", "嚴刑": "엄형",
    "重罰": "중벌"
}

hanja_meaning = {
    "仁": "어질다", "義": "옳다", "禮": "예절",
    "正名": "이름을 바르게 함", "德治": "덕으로 다스림", "無欲": "욕심을 버림",
    "謙虛": "겸손함", "不爭": "다투지 않음", "無爲之治": "인위적이지 않은 정치",
    "反者道之動": "도는 거꾸로 흐른다", "弱者道之用": "약한 것이 오히려 유용하다",
    "慈悲": "사랑과 동정심", "輪廻": "생과 사의 반복", "解脫": "윤회에서 벗어남",
    "中道": "극단을 피하는 삶", "一切唯心造": "모든 것은 마음이 만든다",
    "克己復禮": "욕망을 이기고 예로 돌아감", "克己": "자기 절제",
    "天下": "온 세상", "兼愛": "차별 없는 사랑", "仁義": "인과 의",
    "天長地久": "자연의 도는 오래 간다", "國": "나라", "嚴刑": "엄한 형벌",
    "重罰": "무거운 벌"
}

hanja_list = list(hanja_dict.keys())

# ====================
# 상태 공유 변수
# ====================
q = queue.Queue()
score = 0
running = True
meaning_to_show = ""
show_meaning_until = 0
start_time = time.time()

# 최근 등장한 한자 3개 피하기 위한 리스트
recent_hanjas = []

def get_new_hanja():
    global recent_hanjas
    candidates = [h for h in hanja_list if h not in recent_hanjas]
    if not candidates:
        recent_hanjas = []
        candidates = hanja_list[:]
    new_hanja = random.choice(candidates)
    recent_hanjas.append(new_hanja)
    if len(recent_hanjas) > 3:
        recent_hanjas.pop(0)
    return new_hanja

# 첫 문제 초기화
current_hanja = get_new_hanja()
current_answer = hanja_dict[current_hanja]

# ====================
# Tkinter 입력창
# ====================
def start_tkinter():
    def on_submit(event=None):
        user_input = entry.get().strip()
        q.put(user_input)
        entry.delete(0, tk.END)
        entry.focus_set()

    def on_close():
        global running
        running = False
        root.destroy()

    root = tk.Tk()
    root.title("정답 입력창")

    window_width = 300
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_pos = screen_width - window_width - 20
    y_pos = screen_height - window_height - 150
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    root.attributes('-topmost', True)

    label = tk.Label(root, text="한자 음 입력:", font=("맑은 고딕", 11))
    label.pack(pady=2)

    entry = tk.Entry(root, font=("맑은 고딕", 16))
    entry.pack()
    entry.focus_force()
    entry.bind("<Return>", on_submit)

    result_label = tk.Label(root, text="Enter를 누르세요", font=("맑은 고딕", 11), fg="blue")
    result_label.pack(pady=2)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# ====================
# Pygame 메인 게임
# ====================
def start_pygame():
    global current_hanja, current_answer, score, running, meaning_to_show, show_meaning_until

    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("소나기 게임")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("malgungothic", 72, bold=True)
    small_font = pygame.font.SysFont("malgungothic", 36)

    word_x = random.randint(50, 800)
    word_y = 0
    speed = 1.2
    message = ""
    game_duration = 180  # 3분

    while running:
        elapsed_time = time.time() - start_time
        remaining_time = max(0, int(game_duration - elapsed_time))

        screen.fill((255, 255, 255))

        if elapsed_time >= game_duration:
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            user_input = q.get_nowait()
            if user_input == current_answer:
                score += 1
                message = "정답!"
                meaning_to_show = f"{current_hanja}({current_answer}): {hanja_meaning[current_hanja]}"
                show_meaning_until = time.time() + 3
            else:
                message = "오답!"
                meaning_to_show = ""
            current_hanja = get_new_hanja()
            current_answer = hanja_dict[current_hanja]
            word_x = random.randint(50, 800)
            word_y = 0
        except queue.Empty:
            pass

        word_y += speed
        if word_y > 750:
            current_hanja = get_new_hanja()
            current_answer = hanja_dict[current_hanja]
            word_x = random.randint(50, 800)
            word_y = 0
            message = "시간 초과!"
            meaning_to_show = ""

        hanja_surface = font.render(current_hanja, True, (0, 0, 0), (255, 255, 255))
        screen.blit(hanja_surface, (word_x, word_y))

        score_surface = font.render(f"점수: {score}", True, (0, 128, 0))
        screen.blit(score_surface, (20, 20))

        timer_surface = font.render(f"남은 시간: {remaining_time}s", True, (0, 0, 255))
        screen.blit(timer_surface, (450, 20))

        msg_surface = font.render(message, True, (255, 0, 0))
        screen.blit(msg_surface, (50, 600))

        if meaning_to_show and time.time() < show_meaning_until:
            meaning_surface = small_font.render(meaning_to_show, True, (0, 0, 128))
            screen.blit(meaning_surface, (50, 700))

        pygame.display.flip()
        clock.tick(60)

    # 게임 종료 후 결과 출력
    screen.fill((255, 255, 255))
    final_msg = font.render(f"게임 종료! 최종 점수: {score}", True, (0, 0, 0))
    screen.blit(final_msg, (200, 350))
    pygame.display.flip()
    time.sleep(5)
    pygame.quit()
    # sys.exit() 제거하면 tkinter 꺼지지 않음

# ====================
# 실행
# ====================
if __name__ == "__main__":
    Thread(target=start_tkinter, daemon=True).start()
    start_pygame()
