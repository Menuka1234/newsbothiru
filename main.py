from bs4 import BeautifulSoup
import requests
import time
import telebot
import threading
import os

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
TOKEN = '7750958101:AAE35HmvPt377jA-s30PK9IJflPUR1xmBe8'
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')  # Set parse mode to Markdown

# Replace 'YOUR_GROUP_CHAT_ID' with your actual group chat ID
GROUP_CHAT_ID = '-7197786824'  # Ensure this is the correct group chat ID

# Set to store user chat IDs
user_chat_ids = set()
xox = open("chek.txt","r")
a = int(xox.read().strip())

xox.close()

num = 0

# Function to delete file after a certain delay
def delete_file_after_delay(file_path, delay):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    else:
        print(f"File not found: {file_path}")

# Function to truncate caption if it exceeds Telegram's character limit
def truncate_caption(caption, max_length=1024):
    return caption if len(caption) <= max_length else caption[:max_length - 3] + "..."

# Function to format the description
def format_description(text):
    # Split the text into lines, strip extra spaces, and add 📌 at the start of each line
    lines = text.split('\n')
    formatted_lines = [f"📌 {line.strip()}" for line in lines if line.strip()]
    return '\n'.join(formatted_lines)

# Handle /start command to send a confirmation message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_chat_ids.add(chat_id)
    bot.reply_to(message, f"💫Bot connected successfully!💨")

# Handle all other incoming text messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

# Function to scrape and send news to all users and group
def send_news_to_all():
    global a, num
    while True:
        try:
            link = f"https://www.hirunews.lk/{a}"
            res = requests.get(link)
            so = BeautifulSoup(res.content, "lxml")
            aa = so.find("h1", {"class": "main-tittle"})
            bb = so.find("div", {"id": "article-phara2"})
            cc = so.find("div", {"class": "main-article-banner"})
            dd = cc.find("img") if cc else None
            ff = dd.get("data-src") if dd else None
            a += 1

            if aa and bb and ff:
                num = 0
                xex = open("chek.txt","w")
                xex.write(str(a))
                xex.close()
                # Handle <br> tags in the description
                for br in bb.find_all("br"):
                    br.replace_with("\n")

                title = aa.string
                description = format_description(bb.get_text())  # Format the description
                image_url = ff

                print(f"yes: {title}")

                # Ensure the directory for images exists
                if not os.path.exists('images'):
                    os.makedirs('images')

                # Save image to file
                image_path = os.path.join('images', f"{a}.jpg")
                with open(image_path, "wb") as xx:
                    xx.write(requests.get(image_url).content)

                # Verify that the image is saved correctly
                if os.path.exists(image_path):
                    print(f"Image saved successfully at {image_path}")
                else:
                    print("Failed to save the image")

                # Create the caption with the title in bold
                caption = f"*Title: {title}*\n\n{description}"
                # Truncate the caption if it's too long
                caption = truncate_caption(caption)

                # Send the image with the caption to all users
                for chat_id in user_chat_ids:
                    with open(image_path, "rb") as photo:
                        bot.send_photo(chat_id, photo=photo, caption=caption)
                        print(f"Message sent to user: {chat_id}")

                # Also send the image with the caption to the group
                with open(image_path, "rb") as photo:
                    bot.send_photo(GROUP_CHAT_ID, photo=photo, caption=caption)
                    print(f"Message sent to group: {GROUP_CHAT_ID}")

                # Delete the image after 1 minute
                threading.Thread(target=delete_file_after_delay, args=(image_path, 60)).start()

                
                print(a)
            else:
                print("error404")
                num += 1
                print(num)
                print(a)
                if num == 10:
                    num = 0
                    a -= 10
            

              # Increment to fetch the next article
            time.sleep(1)  # Wait 30 seconds before fetching the next article
        except Exception as e:
            print(f"An error occurred: {e}")

# Start the function in a separate thread to send news updates to all users and group
news_thread = threading.Thread(target=send_news_to_all, daemon=True)
news_thread.start()


bot.polling()

