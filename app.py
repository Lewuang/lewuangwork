from flask import Flask, request
import sqlite3
from datetime import datetime
import calendar

app = Flask(__name__)

# ===== TẠO DATABASE =====

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Bảng tiền
cursor.execute("""
CREATE TABLE IF NOT EXISTS money (
    id INTEGER PRIMARY KEY,
    total INTEGER
)
""")

# Bảng ngày đã chấm công
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT
)
""")

# Bảng lịch sử tháng
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    total INTEGER
)
""")

# Bảng lưu tháng hiện tại
cursor.execute("""
CREATE TABLE IF NOT EXISTS current_month (
    id INTEGER PRIMARY KEY,
    month TEXT
)
""")

# Nếu chưa có tiền
cursor.execute("SELECT * FROM money")
data = cursor.fetchone()

if data is None:
    cursor.execute("INSERT INTO money (id, total) VALUES (1, 0)")

# Nếu chưa có tháng hiện tại
cursor.execute("SELECT * FROM current_month")
month_data = cursor.fetchone()

if month_data is None:

    now = datetime.now()

    current = now.strftime("%m/%Y")

    cursor.execute("""
    INSERT INTO current_month (id, month)
    VALUES (1, ?)
    """, (current,))

conn.commit()
conn.close()

# ===== TRANG CHÍNH =====

@app.route('/')
def home():

    today = datetime.now().strftime("%d/%m/%Y")

    admin = request.args.get("admin")

    current_month_now = datetime.now().strftime("%m/%Y")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ===== KIỂM TRA THÁNG =====

    cursor.execute("SELECT month FROM current_month WHERE id = 1")

    saved_month = cursor.fetchone()[0]

    # Nếu sang tháng mới
    if current_month_now != saved_month:

        # Lấy tổng tiền cũ
        cursor.execute("SELECT total FROM money WHERE id = 1")

        old_total = cursor.fetchone()[0]

        # Lưu lịch sử
        cursor.execute("""
        INSERT INTO history (month, total)
        VALUES (?, ?)
        """, (saved_month, old_total))

        # Reset tiền
        cursor.execute("""
        UPDATE money
        SET total = 0
        WHERE id = 1
        """)

        # Xóa attendance
        cursor.execute("DELETE FROM attendance")

        # Cập nhật tháng mới
        cursor.execute("""
        UPDATE current_month
        SET month = ?
        WHERE id = 1
        """, (current_month_now,))

        conn.commit()

    # ===== LẤY TỔNG TIỀN =====

    cursor.execute("SELECT total FROM money WHERE id = 1")

    total = cursor.fetchone()[0]

    # ===== ĐẾM NGÀY =====

    cursor.execute("SELECT COUNT(*) FROM attendance")

    days = cursor.fetchone()[0]

    # ===== LẤY DANH SÁCH NGÀY =====

    cursor.execute("SELECT date FROM attendance")

    attendance_dates = cursor.fetchall()

    checked_days = []

    for d in attendance_dates:

        date_string = d[0]

        day = int(date_string.split("/")[0])

        checked_days.append(day)

    # ===== TẠO LỊCH =====

    now = datetime.now()

    year = now.year
    month = now.month

    cal = calendar.monthcalendar(year, month)

    calendar_html = """
    <div style="
        margin-top: 40px;
    ">

    <h2 style="
        color: #2b7a78;
        margin-bottom: 20px;
    ">
        Lịch cống hiến
    </h2>

    <div style="
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
    ">
    """

    # Tên thứ
    days_name = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    for name in days_name:

        calendar_html += f"""
        <div style="
            font-weight: bold;
            color: #2b7a78;
        ">
            {name}
        </div>
        """

    # Các ngày
    for week in cal:

        for day in week:

            if day == 0:

                calendar_html += "<div></div>"

            else:

                mark = ""

                # ===== ADMIN MODE =====

                if admin == "lewuang04":

                    if day in checked_days:

                        mark = f"""
                        <a href="/remove/{day}"
                        style="
                            text-decoration:none;
                            font-size:22px;
                            color:red;
                        ">
                            ❌
                        </a>
                        """

                    else:

                        mark = f"""
                        <a href="/add/{day}"
                        style="
                            text-decoration:none;
                            font-size:22px;
                            color:green;
                        ">
                            ⭕
                        </a>
                        """

                else:

                    if day in checked_days:

                        mark = """
                        <div style="
                            color:red;
                            font-size:22px;
                            margin-top:5px;
                        ">
                            ❌
                        </div>
                        """

                calendar_html += f"""
                <div style="
                    background-color: white;
                    border-radius: 15px;
                    height: 70px;
                    padding-top: 8px;
                    box-shadow: 0px 3px 8px rgba(0,0,0,0.08);
                ">

                    <div style="
                        color: #333;
                        font-size: 18px;
                    ">
                        {day}
                    </div>

                    {mark}

                </div>
                """

    calendar_html += "</div></div>"

    # ===== KIỂM TRA HÔM NAY =====

    cursor.execute(
        "SELECT * FROM attendance WHERE date = ?",
        (today,)
    )

    checked = cursor.fetchone()

    # ===== LỊCH SỬ =====

    cursor.execute("""
    SELECT month, total
    FROM history
    ORDER BY id DESC
    """)

    history_data = cursor.fetchall()

    history_html = """
    <div style="
        margin-top: 50px;
    ">

    <h2 style="
        color: #2b7a78;
        margin-bottom: 20px;
    ">
        Lịch sử cống hiến
    </h2>
    """

    for item in history_data:

        month = item[0]
        total_money = item[1]

        history_html += f"""
        <div style="
            background-color: #f5fffd;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 10px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        ">

            <div style="
                color: #2b7a78;
                font-size: 18px;
                font-weight: bold;
            ">
                Tháng {month}
            </div>

            <div style="
                color: #555;
                margin-top: 5px;
            ">
                {total_money:,} VNĐ
            </div>

        </div>
        """

    history_html += "</div>"

    conn.close()

    # ===== NÚT =====

    if checked:

        button = """
        <button disabled
        style="
            background-color: #709c9a;
            color: white;
            padding: 15px 30px;
            font-size: 20px;
            border: none;
            border-radius: 10px;
        ">
            Đã cống hiến
        </button>
        """

    else:

        button = """
        <form action="/conghien">
            <button type="submit"
            style="
                background-color: #3aafa9;
                color: white;
                padding: 15px 30px;
                font-size: 20px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
            ">
                Cống hiến
            </button>
        </form>
        """

    return f"""
<!DOCTYPE html>
<html>

<head>
    <title>Bảng cống hiến</title>
</head>

<body style="
    background-color: #dff7f2;
    font-family: Arial;
    text-align: center;
    padding-top: 100px;
">

    <div style="
        background-color: white;
        width: 700px;
        margin: auto;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
    ">

        <h1 style="
            color: #2b7a78;
            margin-bottom: 30px;
        ">
            Bảng cống hiến
        </h1>

        <h2 style="
            color: #3aafa9;
            margin-bottom: 10px;
        ">
            Số tiền lewuang đã kiếm được: {total:,} VNĐ
        </h2>

        <p style="
            color: #555;
            font-size: 18px;
            margin-bottom: 40px;
        ">
            Đã cống hiến {days} ngày
        </p>

        {button}

        <div style="margin-top:20px;">

            <form action="/" method="GET">

                <input
                    type="password"
                    name="admin"
                    placeholder="Mật khẩu"
                    style="
                        padding:10px;
                        border-radius:10px;
                        border:1px solid #ccc;
                    "
                >

                <button
                    type="submit"
                    style="
                        background-color:#2b7a78;
                        color:white;
                        border:none;
                        padding:10px 15px;
                        border-radius:10px;
                        cursor:pointer;
                    "
                >
                    🔒
                </button>

            </form>

        </div>

        {calendar_html}

        {history_html}

    </div>

</body>

</html>
"""

# ===== THÊM NGÀY =====

@app.route('/add/<int:day>')
def add_day(day):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    month_year = datetime.now().strftime("%m/%Y")

    date_text = f"{day:02d}/{month_year}"

    # kiểm tra tồn tại
    cursor.execute(
        "SELECT * FROM attendance WHERE date = ?",
        (date_text,)
    )

    data = cursor.fetchone()

    if not data:

        cursor.execute("""
        INSERT INTO attendance (date)
        VALUES (?)
        """, (date_text,))

        cursor.execute("""
        UPDATE money
        SET total = total + 250000
        WHERE id = 1
        """)

    conn.commit()
    conn.close()

    return """
    <script>
        window.location.href='/?admin=lewuang04'
    </script>
    """

# ===== XÓA NGÀY =====

@app.route('/remove/<int:day>')
def remove_day(day):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    month_year = datetime.now().strftime("%m/%Y")

    date_text = f"{day:02d}/{month_year}"

    cursor.execute("""
    DELETE FROM attendance
    WHERE date = ?
    """, (date_text,))

    cursor.execute("""
    UPDATE money
    SET total = total - 250000
    WHERE id = 1
    """)

    conn.commit()
    conn.close()

    return """
    <script>
        window.location.href='/?admin=lewuang04'
    </script>
    """

# ===== NÚT CỐNG HIẾN =====

@app.route('/conghien')
def conghien():

    today = datetime.now().strftime("%d/%m/%Y")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # kiểm tra đã bấm chưa
    cursor.execute(
        "SELECT * FROM attendance WHERE date = ?",
        (today,)
    )

    checked = cursor.fetchone()

    if not checked:

        # cộng tiền
        cursor.execute("""
        UPDATE money
        SET total = total + 250000
        WHERE id = 1
        """)

        # lưu ngày
        cursor.execute("""
        INSERT INTO attendance (date)
        VALUES (?)
        """, (today,))

    conn.commit()
    conn.close()

    return """
    <script>
        window.location.href = "/";
    </script>
    """

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)