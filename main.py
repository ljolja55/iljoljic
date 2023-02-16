from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from hashlib import sha256


from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'app'
app.config['MYSQL_PASSWORD'] ='1234'
app.config['MYSQL_DB'] = "seminar"
mysql = MySQL(app)



app.secret_key = '_5#y2L"F4Q8z\n\xec]/'


@app.route('/', methods=['GET'])
def pocetna():
    # print (session['id_uloge'])
    if 'ime' in session:
        if session['uloge'] == 0:
            return redirect(url_for('rezultati1'))
        elif session['uloge'] == 1:
            return redirect(url_for('rezultati'))
    return redirect(url_for('login')), 303



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form.get('email')
        password = sha256(request.form.get('password').encode()).hexdigest()

        query =f"SELECT ime, uloge,id,prezime FROM korisnici_ WHERE HEX(password)='{password}' AND email='{email}'"
        cursor= mysql.connection.cursor()
        cursor.execute(query)
        korisnik=cursor.fetchall()

        if korisnik:
            session['ime'] = korisnik[0][0]
            session['uloge'] = korisnik[0][1]
            session['id'] = korisnik[0][2]
            session['prezime']=korisnik[0][3]
            return redirect(url_for('pocetna')), 303

        else:
            return render_template('login.html', error='Uneseni su krivi korisnički podaci')



@app.route('/index_bpm', methods=['GET'], )
def rezultati():

        id = session['id']
        ime = session['ime']
        prezime = session['prezime']
        if  session['uloge']==0:
            id= request.args.get('id')
            ime = session['ime']
            prezime = session['prezime']





        print(session['id'])
        query = f"SELECT vrijeme, temperatura FROM podatci WHERE korisnik={id} ORDER BY vrijeme  DESC"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        temperature = cursor.fetchall()

        query = f"SELECT ime,prezime FROM korisnici_ WHERE id={id}"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        korisnici = cursor.fetchall()
        podaci=[
            {
                'ime':korisnici[0][0],
                'prezime':korisnici[0][1]
            }
        ]

        data_zadnji = [

            {
                'vrijeme': f'{temperature[0][0]}',
                'vrijednost': f'{temperature[0][1]}'
            },
            {
                'vrijeme': f'{temperature[1][0]}',
                'vrijednost': f'{temperature[1][1]}',
            },
            {
                'vrijeme': f'{temperature[2][0]}',
                'vrijednost': f'{temperature[2][1]}',
            },
            {
                'vrijeme': f'{temperature[3][0]}',
                'vrijednost': f'{temperature[3][1]}',
            },
            {
                'vrijeme': f'{temperature[4][0]}',
                'vrijednost': f'{temperature[4][1]}',
            },
            {
                'vrijeme': f'{temperature[5][0]}',
                'vrijednost': f'{temperature[5][1]}',
            },
            {
                'vrijeme': f'{temperature[6][0]}',
                'vrijednost': f'{temperature[6][1]}',
            },
            {
                'vrijeme': f'{temperature[7][0]}',
                'vrijednost': f'{temperature[7][1]}',
            },
            {
                'vrijeme': f'{temperature[8][0]}',
                'vrijednost': f'{temperature[8][1]}',
            },
            {
                'vrijeme': f'{temperature[9][0]}',
                'vrijednost': f'{temperature[9][1]}',
            }
        ]
        query = f"SELECT vrijeme, bpm FROM podatci WHERE korisnik={id} ORDER BY vrijeme  DESC"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        otkucaji = cursor.fetchall()
        data_top = [
            {
                'vrijeme': f'{otkucaji[0][0]}',
                'vrijednost': f'{otkucaji[0][1]}',
            },
            {
                'vrijeme': f'{otkucaji[1][0]}',
                'vrijednost': f'{otkucaji[1][1]}',
            },
            {
                'vrijeme': f'{otkucaji[2][0]}',
                'vrijednost': f'{otkucaji[2][1]}',
            },
            {
                'vrijeme': f'{otkucaji[3][0]}',
                'vrijednost': f'{otkucaji[3][1]}',
            },
            {
                'vrijeme': f'{otkucaji[4][0]}',
                'vrijednost': f'{otkucaji[4][1]}',
            },
            {
                'vrijeme': f'{otkucaji[5][0]}',
                'vrijednost': f'{otkucaji[5][1]}',
            },
            {
                'vrijeme': f'{otkucaji[6][0]}',
                'vrijednost': f'{otkucaji[6][1]}',
            },
            {
                'vrijeme': f'{otkucaji[7][0]}',
                'vrijednost': f'{otkucaji[7][1]}',
            },
            {
                'vrijeme': f'{otkucaji[8][0]}',
                'vrijednost': f'{otkucaji[8][1]}',
            },
            {
                'vrijeme': f'{otkucaji[9][0]}',
                'vrijednost': f'{otkucaji[9][1]}',
            }
        ]
        return render_template('index_bpm.html', data_zadnji=data_zadnji, data_top=data_top,podaci=podaci), 303

@app.route('/funkcije', methods=[ 'POST'])
def funkcije():

        json=request.get_json()
        bpm=(json['bpm'])
        temperatura=(json['temperatura'])

        query= f"INSERT INTO podatci(vrijeme,bpm,temperatura) VALUES(NOW(),{bpm},{temperatura})"
        cursor= mysql.connection.cursor()
        cursor.execute(query)

        mysql.connection.commit()
        print (bpm)
        return "pl"




@app.route('/nazad', methods=['GET'])
def nazad():
     return redirect(url_for('pocetna')), 303

@app.route('/index', methods=['GET'], )
def rezultati1():
    query = f"SELECT  id,ime, prezime FROM korisnici_ WHERE uloge=1"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    korisnicii = cursor.fetchall()

    query = f"SELECT vrijeme, temperatura FROM podatci WHERE korisnik=1 ORDER BY vrijeme  DESC"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    temperature = cursor.fetchall()

    query = f"SELECT vrijeme, temperatura FROM podatci WHERE korisnik=2 ORDER BY vrijeme  DESC"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    temperature2 = cursor.fetchall()

    query = f"SELECT ime,prezime FROM korisnici_"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    korisnici = cursor.fetchall()
    podaci=[
            {
                'ime':korisnici[0][0],
                'prezime':korisnici[0][1],
                'ime2': korisnici[1][0],
                'prezime2': korisnici[1][1]
            }
        ]

    data_zadnji = [

            {
                'vrijeme': f'{temperature[0][0]}',
                'vrijednost': f'{temperature[0][1]}'
            },
            {
                'vrijeme': f'{temperature[1][0]}',
                'vrijednost': f'{temperature[1][1]}',
            },
            {
                'vrijeme': f'{temperature[2][0]}',
                'vrijednost': f'{temperature[2][1]}',
            },
            {
                'vrijeme': f'{temperature[3][0]}',
                'vrijednost': f'{temperature[3][1]}',
            },
            {
                'vrijeme': f'{temperature[4][0]}',
                'vrijednost': f'{temperature[4][1]}',
            },
            {
                'vrijeme': f'{temperature[5][0]}',
                'vrijednost': f'{temperature[5][1]}',
            },
            {
                'vrijeme': f'{temperature[6][0]}',
                'vrijednost': f'{temperature[6][1]}',
            },
            {
                'vrijeme': f'{temperature[7][0]}',
                'vrijednost': f'{temperature[7][1]}',
            },
            {
                'vrijeme': f'{temperature[8][0]}',
                'vrijednost': f'{temperature[8][1]}',
            },
            {
                'vrijeme': f'{temperature[9][0]}',
                'vrijednost': f'{temperature[9][1]}',
            }
        ]
    data_zadnji2 = [

        {
            'vrijeme': f'{temperature2[0][0]}',
            'vrijednost': f'{temperature2[0][1]}'
        },
        {
            'vrijeme': f'{temperature2[1][0]}',
            'vrijednost': f'{temperature2[1][1]}',
        },
        {
            'vrijeme': f'{temperature2[2][0]}',
            'vrijednost': f'{temperature2[2][1]}',
        },
        {
            'vrijeme': f'{temperature2[3][0]}',
            'vrijednost': f'{temperature2[3][1]}',
        },
        {
            'vrijeme': f'{temperature2[4][0]}',
            'vrijednost': f'{temperature2[4][1]}',
        },
        {
            'vrijeme': f'{temperature2[5][0]}',
            'vrijednost': f'{temperature2[5][1]}',
        },
        {
            'vrijeme': f'{temperature2[6][0]}',
            'vrijednost': f'{temperature2[6][1]}',
        },
        {
            'vrijeme': f'{temperature2[7][0]}',
            'vrijednost': f'{temperature2[7][1]}',
        },
        {
            'vrijeme': f'{temperature2[8][0]}',
            'vrijednost': f'{temperature2[8][1]}',
        },
        {
            'vrijeme': f'{temperature2[9][0]}',
            'vrijednost': f'{temperature2[9][1]}',
        }
    ]
    query = f"SELECT vrijeme, bpm FROM podatci WHERE korisnik=1 ORDER BY vrijeme  DESC"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    otkucaji = cursor.fetchall()
    data_top= [
        {
            'vrijeme': f'{otkucaji[0][0]}',
            'vrijednost': f'{otkucaji[0][1]}',
        },
        {
            'vrijeme': f'{otkucaji[1][0]}',
            'vrijednost': f'{otkucaji[1][1]}',
        },
        {
            'vrijeme': f'{otkucaji[2][0]}',
            'vrijednost': f'{otkucaji[2][1]}',
        },
        {
            'vrijeme': f'{otkucaji[3][0]}',
            'vrijednost': f'{otkucaji[3][1]}',
        },
        {
            'vrijeme': f'{otkucaji[4][0]}',
            'vrijednost': f'{otkucaji[4][1]}',
        },
        {
            'vrijeme': f'{otkucaji[5][0]}',
            'vrijednost': f'{otkucaji[5][1]}',
        },
        {
            'vrijeme': f'{otkucaji[6][0]}',
            'vrijednost': f'{otkucaji[6][1]}',
        },
        {
            'vrijeme': f'{otkucaji[7][0]}',
            'vrijednost': f'{otkucaji[7][1]}',
        },
        {
            'vrijeme': f'{otkucaji[8][0]}',
            'vrijednost': f'{otkucaji[8][1]}',
        },
        {
            'vrijeme': f'{otkucaji[9][0]}',
            'vrijednost': f'{otkucaji[9][1]}',
        }
    ]

    query = f"SELECT vrijeme, bpm FROM podatci WHERE korisnik=2 ORDER BY vrijeme  DESC"
    cursor = mysql.connection.cursor()
    cursor.execute(query)
    otkucaji2 = cursor.fetchall()
    data_top2 = [
            {
                'vrijeme': f'{otkucaji2[0][0]}',
                'vrijednost': f'{otkucaji2[0][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[1][0]}',
                'vrijednost': f'{otkucaji2[1][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[2][0]}',
                'vrijednost': f'{otkucaji2[2][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[3][0]}',
                'vrijednost': f'{otkucaji2[3][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[4][0]}',
                'vrijednost': f'{otkucaji2[4][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[5][0]}',
                'vrijednost': f'{otkucaji2[5][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[6][0]}',
                'vrijednost': f'{otkucaji2[6][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[7][0]}',
                'vrijednost': f'{otkucaji2[7][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[8][0]}',
                'vrijednost': f'{otkucaji2[8][1]}',
            },
            {
                'vrijeme': f'{otkucaji2[9][0]}',
                'vrijednost': f'{otkucaji2[9][1]}',
            }
        ]
    return render_template('index.html', data_zadnji=data_zadnji, data_top=data_top, podaci=podaci, korisnici=korisnici, korisnicii=korisnicii, data_zadnji2=data_zadnji2, data_top2=data_top2), 303





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)
