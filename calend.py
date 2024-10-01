import pytesseract
import cv2
import time
from datetime import datetime, timedelta
from plyer import notification

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    return thresh

def extract_text_from_image(image_path):
    preprocessed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(preprocessed_img)
    return text

def notify_user(med_name, dose, reminder_time):
    notification.notify(
        title='Medication Reminder',
        message=f'Time to take your medication: {med_name} ({dose} mg)',
        app_name='Medication Reminder',
        timeout=10
    )
    print(f"Notification: Time to take {med_name} ({dose} mg) at {reminder_time.strftime('%Y-%m-%d %H:%M')}.")

def schedule_medication(med_name, dose, frequency_hours, duration_days):
    start_time = datetime.now()
    reminders = []
    
    for i in range(int(24 / frequency_hours) * duration_days):
        reminder_time = start_time + timedelta(hours=i * frequency_hours)
        reminders.append((reminder_time, med_name, dose))
    
    return reminders

def process_reminders(reminders):
    while True:  # Infinite loop to keep sending reminders
        for reminder_time, med_name, dose in reminders:
            current_time = datetime.now()
            if current_time >= reminder_time:
                notify_user(med_name, dose, reminder_time)
                # Schedule next reminder
                reminder_time += timedelta(hours=8)  # Change this to desired frequency
                reminders.append((reminder_time, med_name, dose))
                reminders.remove((reminder_time - timedelta(hours=8), med_name, dose))  # Remove old reminder

        time.sleep(60)  # Check every minute

def parse_prescription_text(extracted_text):
    med_name, dose, frequency_hours, duration_days = None, None, 8, 3  # Default values

    lines = extracted_text.splitlines()
    for line in lines:
        if "Medication:" in line:
            med_name = line.split(":")[1].strip()
        elif "Dosage:" in line:
            dose = int(line.split(":")[1].strip().split()[0])  # Extract dosage
        elif "Frequency:" in line:
            frequency_parts = line.split(":")[1].strip().split()
            for part in frequency_parts:
                if part.isdigit():
                    frequency_hours = int(part)
                    break
        elif "Duration:" in line:
            duration_days = int(line.split(":")[1].strip().split()[0])  # Extract duration

    return med_name or "Unknown Medication", dose or 500, frequency_hours, duration_days

def process_prescription(image_path):
    extracted_text = extract_text_from_image(image_path)
    print("Extracted Text:\n", extracted_text)

    med_name, dose, frequency_hours, duration_days = parse_prescription_text(extracted_text)

    print(f"Medication Name: {med_name}")
    print(f"Dosage: {dose} mg")
    print(f"Frequency: Every {frequency_hours} hours")
    print(f"Duration: {duration_days} days")

    reminders = schedule_medication(med_name, dose, frequency_hours, duration_days)
    process_reminders(reminders)

if __name__ == "__main__":
    image_path = input("Enter the path to the prescription image: ")
    process_prescription(image_path)
