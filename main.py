from sqlite3.dbapi2 import Cursor
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QLineEdit, QMainWindow, QWidget
import sqlite3
from PyQt5 import QtWidgets
import pyqtgraph as pg

class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui",self)
        
        self.Button_signIn.clicked.connect(self.openLogin)
        self.Button_register.clicked.connect(self.openRegister)

    def openLogin(self):
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def openRegister(self):
        register = registerScreen()
        widget.addWidget(register)
        widget.setCurrentIndex(widget.currentIndex()+1)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("login.ui",self)
        self.Button_home.clicked.connect(self.openWelcome)
        self.Button_login.clicked.connect(self.login)
        #Hide password
        self.lineEdit_password.setEchoMode(QLineEdit.Password)

    def openWelcome(self):
        welcome = WelcomeScreen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def openMain(self):
        main = mainScreen()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def userId(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        data = (username,password)
        cursor.execute("SELECT id FROM users WHERE username=? and password=?",data)
        id = cursor.fetchone()
        LoginScreen.userId.id = id[0]

    def login(self):
        global username
        global password
        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        data = (username, password)
        #fetch data accordingly
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? and password=?",data)
        user = cursor.fetchone()
        if user is None:
            self.label_notification.setText('Invalid username or password')
        else:
            self.openMain()


        conn.close()
        

class registerScreen(QDialog):
    def __init__(self):
        super(registerScreen, self).__init__()
        loadUi("register.ui",self)

        #add functions to buttons and hide passwords
        self.Button_collect.clicked.connect(self.registerCollect)
        self.Button_home.clicked.connect(self.openWelcome)
        self.lineEdit_password.setEchoMode(QLineEdit.Password)
        self.lineEdit_confirmPassword.setEchoMode(QLineEdit.Password)

    def openWelcome(self):
        welcome = WelcomeScreen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def openMain(self):
        main = mainScreen()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex()+1)

    #Collect register data and input it to database
    def registerCollect(self):
        global username
        global password
        #connect to user database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        cpassword = self.lineEdit_confirmPassword.text()

        #Check is database already contains a same named user.
        cursor.execute("SELECT * FROM users WHERE username=?",(username,))
        u = cursor.fetchone()
        if u is None:
            #check if password is the same as confirmed password
            if password == cpassword:
                cursor.execute("SELECT id FROM users ORDER BY id DESC LIMIT 1")
                results = cursor.fetchone()
                id = int(results[0]) + 1
                #Add new user to database
                cursor.execute("INSERT INTO users VALUES (:username, :password, :id)",
                {
                'username': username,
                'password': password,
                'id': id
                })

                conn.commit()
                conn.close()

                self.openMain()
            else:
                self.label_notification.setText('Invalid passwords')
        else:
            self.label_notification.setText('Username is taken')
class mainScreen(QMainWindow):
    # dictionary for exercises and their ids
    exercise_dict = {
        1:'Squat',
        2:'Bench Press',
        3:'Incline Dumbbell Press',
        4:'Deadlift',
        5:'Leg Extension',
        6:'Leg Curl',
        7:'Chest Fly',
        8:'Peck Deck',
        9:'Pullover',
        10:'Lat Pulldown',
        11:'Row machine',
        12:'Tricep Pushdown',
        13:'Bicep Curl'
    }
    
    def __init__(self):
        global id
        super(mainScreen, self).__init__()
        loadUi("mainWindow.ui",self)

        #add functions to buttons
        self.Button_search.clicked.connect(self.search)
        self.Button_add.clicked.connect(self.add)
        self.Button_clear.clicked.connect(self.entriesSetDefault)
        self.calendarWidget.selectionChanged.connect(lambda : self.customEvent('Change'))
        self.comboBox7.currentTextChanged.connect(self.plot)

        #add functions to menu bar
        self.actionLog_out.triggered.connect(self.openWelcome)
        self.actionClose.triggered.connect(lambda : sys.exit(app.exec))
        
        #add plot background and labels
        self.graphWidget.setBackground('w')
        self.graphWidget.setLabel('left', 'Weight(KG)', color = 'r', size = '12pt')
        self.graphWidget.setLabel('bottom', 'Training session', color = 'r', size = '12pt')

        #Add items to dropboxes
        data = ['Select Exercise','Squat', 'Bench Press', 'Incline Dumbbell Press', 'Deadlift', 'Leg Extension', 'Leg Curl', 'Chest Fly', 'Peck Deck', 'Pullover', 'Lat Pulldown', 'Row machine',
                'Tricep Pushdown', 'Bicep Curl']
        self.comboBox1.addItems(data)
        self.comboBox2.addItems(data)
        self.comboBox3.addItems(data)
        self.comboBox4.addItems(data)
        self.comboBox5.addItems(data)
        self.comboBox6.addItems(data)
        self.comboBox7.addItems(data)
        

        #UserId
        LoginScreen.userId(self)
        id = LoginScreen.userId.id

        self.dateUpdate()

        #Fill listWidget
        self.fillList()
        self.personalBests()
    
    #function to open welcome screen after logging out.
    def openWelcome(self):
        welcome = WelcomeScreen()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)

    #Check if calendar date has been changed
    def customEvent(self,e):
        self.dateUpdate()
        self.search()

    #Update date lineEdit if event has happened
    def dateUpdate(self):
        d1 = str(self.calendarWidget.selectedDate())
        date = d1.replace('PyQt5.QtCore.QDate', "")
        date = date.replace('(', "")
        date = date.replace(')', "")
        date = date.replace(' ', '')
        x = date.split(",")
        date  = x[2] + "/" + x[1] + "/" + x[0]
        self.lineEdit_date.setText(str(date))


    #Fill workout list with the dates of workouts
    def fillList(self):
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()
        #select all items from the user
        cursor.execute("SELECT date FROM workouts WHERE id=? ORDER BY substr (date,0,2) || substr (date,3,5) || substr (date,6,9) DESC", (id,))
        rows = cursor.fetchall()
        for i in reversed(rows):
            self.listWidget.addItem(i[0])


    def exercises(self):
        #get exercises and change all spaces to _ so they are easily accessible 
        #in workouts database
        exercises = (
            self.comboBox1.currentText().replace(" ","_"),
            self.comboBox2.currentText().replace(" ","_"),
            self.comboBox3.currentText().replace(" ","_"),
            self.comboBox4.currentText().replace(" ","_"),
            self.comboBox5.currentText().replace(" ","_"),
            self.comboBox6.currentText().replace(" ","_")
        )

        #make exercises to string that can be used in sqlite3
        number = 0
        string = "INSERT INTO workouts("
        string = string + 'id' + ','
        string = string + 'date' + ','
        for i in exercises:
            if number==0:
                string = string + i + ','
            elif number==5:
                string = string + i + ')'
            else:
                string = string + i + ','
            number += 1
        
        string = string + ' VALUES (?,?,?,?,?,?,?,?)'
        return string

    def entriesSetDefault(self):
        self.comboBox1.setCurrentIndex(0)
        self.comboBox2.setCurrentIndex(0)
        self.comboBox3.setCurrentIndex(0)
        self.comboBox4.setCurrentIndex(0)
        self.comboBox5.setCurrentIndex(0)
        self.comboBox6.setCurrentIndex(0)

        self.spinBox1.setValue(0)
        self.spinBox2.setValue(0)
        self.spinBox3.setValue(0)
        self.spinBox4.setValue(0)
        self.spinBox5.setValue(0)
        self.spinBox6.setValue(0)

        self.lineEdit1.setText('')
        self.lineEdit2.setText('')
        self.lineEdit3.setText('')
        self.lineEdit4.setText('')
        self.lineEdit5.setText('')
        self.lineEdit6.setText('')

    #Search workout by id and date. Then update the data.
    def search(self):
        date = self.lineEdit_date.text()
        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()
        data = (id, date)

        #Search database by id and data
        cursor.execute("SELECT * FROM workouts WHERE id=? and date=?", data)
        rows = cursor.fetchall()
        try: 
            rep_weight, ids = self.removeNONEs(rows[0])

            #gets reps and weight seperately
            rep_weight[0].split('-')

            # fill data
            self.comboBox1.setCurrentIndex(ids[0])
            self.comboBox2.setCurrentIndex(ids[1])
            self.comboBox3.setCurrentIndex(ids[2])
            self.comboBox4.setCurrentIndex(ids[3])
            self.comboBox5.setCurrentIndex(ids[4])
            self.comboBox6.setCurrentIndex(ids[5])

            self.spinBox1.setValue(int(rep_weight[0].split('-')[0]))
            self.spinBox2.setValue(int(rep_weight[1].split('-')[0]))
            self.spinBox3.setValue(int(rep_weight[2].split('-')[0]))
            self.spinBox4.setValue(int(rep_weight[3].split('-')[0]))
            self.spinBox5.setValue(int(rep_weight[4].split('-')[0]))
            self.spinBox6.setValue(int(rep_weight[5].split('-')[0]))

            self.lineEdit1.setText(rep_weight[0].split('-')[1])
            self.lineEdit2.setText(rep_weight[1].split('-')[1])
            self.lineEdit3.setText(rep_weight[2].split('-')[1])
            self.lineEdit4.setText(rep_weight[3].split('-')[1])
            self.lineEdit5.setText(rep_weight[4].split('-')[1])
            self.lineEdit6.setText(rep_weight[5].split('-')[1])
        except:
            pass



        #Remove nones from rows for search function
    def removeNONEs(self, rows):
        exercises_reps_weight = []
        exercisesId = []
        number = 1
        cycle = 0

        #use cylce and number variables to keep track of the loop cycles
        #and how many exercises have been gone through
        for i in rows:
            if i is not None and cycle > 1:
                exercises_reps_weight.append(i)
                exercisesId.append(number)
                number += 1
            elif i is None and cycle > 1:
                number += 1
            cycle += 1
        return exercises_reps_weight, exercisesId
                


    #Add new workout to database
    def add(self):
        date = self.lineEdit_date.text()

        #Reps - weight
        values = (
            id,
            date,
            str(self.spinBox1.value()) + '-' + self.lineEdit1.text(),
            str(self.spinBox2.value()) + '-' + self.lineEdit2.text(),
            str(self.spinBox3.value()) + '-' + self.lineEdit3.text(),
            str(self.spinBox4.value()) + '-' + self.lineEdit4.text(),
            str(self.spinBox5.value()) + '-' + self.lineEdit5.text(),
            str(self.spinBox6.value()) + '-' + self.lineEdit6.text()
        )

        sql = self.exercises()

        conn = sqlite3.connect('workouts.db')
        cursor = conn.cursor()
        cursor.execute(sql,values)
        conn.commit()
        cursor.close()
        self.entriesSetDefault()
        self.personalBests()
        self.fillList()

    def personalBests(self):
        try:
            conn = sqlite3.connect('workouts.db')
            cursor = conn.cursor()
            cursor.execute("SELECT Squat, Bench_Press, Deadlift FROM workouts WHERE id=?", (id,))
            rows = cursor.fetchall()
            #loop through rows to find the heaviest squat done.
            squatPB = 0
            squat = ''
            benchPB = 0
            bench = ''
            deadliftPB = 0
            deadlift = ''
            for i in rows:
                if i[0] is not None:
                    if int(i[0].split('-')[1]) > int(squatPB):
                        squatPB = i[0].split('-')[1]
                        squat = i[0]
                if i[1] is not None:
                    if int(i[1].split('-')[1]) > int(benchPB):
                        benchPB = i[1].split('-')[1]
                        bench = i[1]
                if i[2] is not None:
                    if int(i[2].split('-')[1]) > int(deadliftPB):
                        deadliftPB = i[2].split('-')[1]
                        deadlift = i[2]

            #add personal best data to lineEdits.
            if squat != '':
                self.lineEdit_pbSquat.setText(squat.split('-')[1]+'kg for ' + squat.split('-')[0])
            if bench != '':
                self.lineEdit_pbBench.setText(bench.split('-')[1]+'kg for ' + bench.split('-')[0])
            if deadlift != '':
                self.lineEdit_pbDeadlift.setText(deadlift.split('-')[1]+'kg for ' + deadlift.split('-')[0]) 

        #if there is no prior data then do nothing        
        except:
            pass

    def plot(self):
        try: 
            self.graphWidget.clear()
            self.label_plot.setText('')
            conn = sqlite3.connect('workouts.db')
            cursor = conn.cursor()

            exercise = self.comboBox7.currentText().replace(' ', '_')
            sql = "SELECT " + exercise + ", date FROM workouts where id =? ORDER BY substr (date,0,2) || substr (date,3,5) || substr (date,6,9) DESC"
            cursor.execute(sql, (id,))
            rows = cursor.fetchall()

            #weight and workouts contains the data from database
            weight = []
            workouts = []

            #append from rows to weight list
            workout = 1
            for i in rows:
                w= int(i[0].split('-')[1])
                weight.append(w)
                workouts.append(workout)
                workout += 1

            #plot graph
            self.graphWidget.plot(workouts, weight, symbol='o')
            styles = {"color": "b", "font-size": "15px"}
            self.graphWidget.setTitle("Your " + self.comboBox7.currentText() + " progression", **styles)
            
            #set range based on data
            max = weight[len(weight)-1]
            self.graphWidget.setXRange(0, len(workouts)+2, padding=0)
            self.graphWidget.setYRange(0, max+10, padding=0)
        except:
            if self.comboBox7.currentText() != 'Select Exercise':
                self.label_plot.setText('No data on this exercise')


#main

app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(576)
widget.setFixedWidth(1024)
widget.show()
try:
    sys.exit(app.exec_())
except:
    pass