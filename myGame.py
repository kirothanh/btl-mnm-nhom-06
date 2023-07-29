import cv2
import pyautogui 
from myPose import myPose
from datetime import datetime

class myGame():
    def __init__(self):
        self.pose = myPose()
        self.game_started = False
        self.x_position = 1 # 0: Ray ben trai, 1: Ray giua, 2: Ray ben phai
        self.y_position = 1 # 0: Down, 1: Stand, 2: jump
        self.clap_duration = 0 # So frame ma ng dung vo tay
        self.score = self.load_score_from_file()  # Load the previous score from file
        self.switch_duration = 0 # So frame ma nguoi dung chuyen doi tu the tay giua khong chuyen dong va vo tay

    def load_score_from_file(self, filename="score.txt"):
        try:
            with open(filename, "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0
        except Exception as e:
            print("Error loading the score:", str(e))
            return 0

    def move_LRC(self, LRC):
        if LRC=="L":
            for _ in range(self.x_position):
                pyautogui.press('left')
            self.x_position = 0
        elif LRC=="R":
            for _ in range(2, self.x_position, -1):
                pyautogui.press('right')
            self.x_position = 2
        else:
            if self.x_position ==0:
                pyautogui.press('right')
            elif self.x_position == 2:
                pyautogui.press('left')

            self.x_position = 1
        return

    def move_JSD(self, JSD):
        if (JSD=="J") and (self.y_position == 1):
            pyautogui.press('up')
            self.y_position = 2
        elif (JSD=="D") and (self.y_position ==1):
            pyautogui.press('down')
            self.y_position = 0
        elif (JSD=="S") and (self.y_position !=1):
            self.y_position = 1
        return

    def play(self):

        # Khoi tao camera
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 960)

        while True:
            ret, image = cap.read()
            if ret:

                image = cv2.flip(image, 1)
                image_height, image_width, _ = image.shape
                image, results = self.pose.detectPose(image)

                if results.pose_landmarks:
                    # Kiem tra game da bat dau chua
                    if self.game_started:
                        # Kiem tra trai phai
                        image, LRC = self.pose.checkPose_LRC(image, results)
                        self.move_LRC(LRC)

                        # Kiem tra len xuong
                        image, JSD = self.pose.checkPose_JSD(image, results)
                        self.move_JSD(JSD)
                    else:
                        cv2.putText(image, "Clap your hand to start!", (5, image_height-10), cv2.FONT_HERSHEY_PLAIN, 2, (255,255,0), 3)

                    image, CLAP = self.pose.checkPose_Clap(image, results)
                    if CLAP == "C":
                        self.clap_duration +=1

                        if self.clap_duration == 10: #10 frame
                            if self.game_started:
                                # Reset
                                self.x_position  = 1
                                self.y_position  = 1
                                self.pose.save_shoulder_line_y(image, results)
                                pyautogui.press('space')
                            else:
                                self.game_started  = True
                                self.pose.save_shoulder_line_y(image, results)
                                pyautogui.click(x=720, y = 560, button = "left")

                                self.score += 1  # Increase the score by 1 each time the game starts

                            self.clap_duration = 0
                    
                    elif CLAP == "SW":
                        self.switch_duration += 1
                    else:
                        self.clap_duration = 0


                cv2.imshow("Game", image)
                cv2.waitKey(1)

            if self.switch_duration == 20:
                break

        self.save_score_to_file()  # Save the player's score when the game ends
        cap.release()
        cv2.destroyAllWindows()

    def save_score_to_file(self, filename="score.txt"):
        try:
            with open(filename, "a") as file:  # Use "a" (append) mode to add scores to a new line
                print("\n")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time
                score_data = f"{current_time}: {self.score}\n"  # Format the score data
                file.write(score_data)  # Write the score data to the file
            print("Score saved successfully.")
        except Exception as e:
            print("Error saving the score:", str(e))


myGame = myGame()
myGame.play()