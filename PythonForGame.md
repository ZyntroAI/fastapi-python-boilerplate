---
aliases:
  - Game
---
import turtle
import time
import random

# ตั้งค่าความเร็วของเกม (ยิ่งน้อยยิ่งเร็ว)
delay = 0.1

# คะแนนเริ่มต้น
score = 0
high_score = 0

# 1. ตั้งค่าหน้าจอเกม
wn = turtle.Screen()
wn.title("Snake Game by AI")
wn.bgcolor("black")
wn.setup(width=600, height=600)
wn.tracer(0) # ปิดการอัปเดตหน้าจออัตโนมัติเพื่อความลื่นไหล

# 2. สร้างหัวงู
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("green")
head.penup()
head.goto(0, 0)
head.direction = "stop"

# 3. สร้างอาหารงู
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

segments = []

# 4. ส่วนแสดงคะแนน
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

# 5. ฟังก์ชันควบคุมทิศทาง
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

# รับคำสั่งจากคีย์บอร์ด
wn.listen()
wn.onkeypress(go_up, "Up")
wn.onkeypress(go_down, "Down")
wn.onkeypress(go_left, "Left")
wn.onkeypress(go_right, "Right")

# 6. Loop หลักของเกม (Main Game Loop)
while True:
    wn.update()

    # ตรวจสอบการชนขอบหน้าจอ (Game Over)
    if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290:
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"

        # ซ่อนส่วนหางเมื่อเริ่มใหม่
        for segment in segments:
            segment.goto(1000, 1000)
        segments.clear()

        # รีเซ็ตคะแนน
        score = 0
        delay = 0.1
        pen.clear()
        pen.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

    # ตรวจสอบเมื่อกินอาหาร
    if head.distance(food) < 20:
        # สุ่มตำแหน่งอาหารใหม่
        x = random.randint(-280, 280)
        y = random.randint(-280, 280)
        food.goto(x, y)

        # เพิ่มข้อต่อหางงู
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("lightgreen")
        new_segment.penup()
        segments.append(new_segment)

        # เพิ่มความเร็วเกมเล็กน้อย
        delay -= 0.003

        # เพิ่มคะแนน
        score += 10
        if score > high_score:
            high_score = score
        
        pen.clear()
        pen.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

    # เคลื่อนที่ส่วนหางตามหัว (ไล่จากท้ายสุดมาหน้า)
    for index in range(len(segments) - 1, 0, -1):
        x = segments[index - 1].xcor()
        y = segments[index - 1].ycor()
        segments[index].goto(x, y)

    # ให้หางชิ้นแรกสุดวิ่งตามหัว
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    move()

    # ตรวจสอบการชนหางตัวเอง (Game Over)
    for segment in segments:
        if segment.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "stop"
            
            for seg in segments:
                seg.goto(1000, 1000)
            segments.clear()
            
            score = 0
            delay = 0.1
            pen.clear()
            pen.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))

    time.sleep(delay)

wn.mainloop()
