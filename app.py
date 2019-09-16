import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session, Markup
from flask_session import Session
# from . import main

from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from operator import itemgetter
from functools import wraps

# this is the helper functions, one with the microsoft sql database, and one with the googlesheet database 
from sqlhelper import permit_avg, get_servicio_numbre_list, get_permiso_numbre_list, find_servicio_id, find_permiso_id, get_gps_data, get_legal_data, find_permit_month, find_permit_duration, find_project_duration, find_project_all, seperate, cvt_light, cvt_light_easier, inv_block, find_permit_all,get_max_sid, get_env
from gsheethelper import get_super_all, get_super_servicio, get_alineacion_all, get_recom_all, get_recom_servicio, get_sin_gps



# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.errorhandler(404)
def error_404(error):
    return render_template('error_404.html')


@app.errorhandler(Exception)
def error_500(error):
    """这个handler可以catch住所有的abort(500)和raise exeception."""
    return render_template('error_500.html')

def apology(message):
    """Render message as an apology to user."""
    return render_template("apology.html", send_message=message)


def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# here I am defining some global variables
time_now = datetime.now()
time_now_nomicro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
year_2dig = int((str(time_now.year))[2:4])
month_2dig = time_now.month
user_id = 1

servicio_nu = 1 
servicio_id = 1
permiso_nu = 1 
permiso_id = 1
permit_dataset = [0, 0, 0]

servicio_numbre_list = get_servicio_numbre_list(999)

all_names_permisos = []
all_names_servicios = []

permiso_light_list = []
super_light_list = []
alineacion_light_list = []


def refresh_website():
    global time_now, time_now_nomicro, year_2dig, month_2dig, servicio_nu, servicio_id, permiso_nu, permiso_id, permit_dataset, servicio_numbre_list, all_names_permisos, all_names_servicios, permiso_light_list, super_light_list, alineacion_light_list
    time_now = datetime.now()
    time_now_nomicro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    year_2dig = int((str(time_now.year))[2:4])
    month_2dig = time_now.month

    servicio_nu = 1 
    servicio_id = 1
    permiso_nu = 1 
    permiso_id = 1
    permit_dataset = [0, 0, 0]

    servicio_numbre_list = get_servicio_numbre_list(999)
    all_names_permisos = []
    all_names_servicios = []

    permiso_light_list = []
    super_light_list = []
    alineacion_light_list = []    


def pid_list(x): ### this doesn't seem very automatic 
        if x == 11:
            return [1,2]
        else:
            return (list(range(1, 30)))

max_sid = get_max_sid()
sid_list = (list(range(1, max_sid))) 
sid_list_no_sea = sid_list
sid_list_no_sea.remove(11) #here i am defining a list that has no sid=11 which is SEA, this will be used in the permiso/rank part

def sort_lists(lists, a):
    item = 1
    for item in lists:
        if (item[a])== 'Green':
            item.append(3)
        elif (item[a]) == 'Yellow':
            item.append(2)
        else:
            item.append(1)
    return sorted(lists, key=itemgetter(len(lists[0])-1))    


#Here is where the real functions start
@app.route("/login", methods=["GET", "POST"])
# from the course's TF
def login():
    global user_id
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "GET":
        return render_template("login.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        if (request.form.get("username")) != "**********" or (request.form.get("password")) != "**********":
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = user_id 
        print ("user_id: "+ str(user_id) +"at "+ str(datetime.now()))
        user_id += 1 

        # Redirect user to home page
        return redirect("/")



@app.route("/logout")
# from TF
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
@login_required
def home():
    global permiso_light_list, super_light_list, alineacion_light_list
    permiso_light_list = []
    super_light_list = []
    alineacion_light_list = (get_alineacion_all(1))[0]

    # for all the permits
    for item in sid_list:
        temp = get_gps_data(item, 999)
        if temp[0] == 0 or temp[1] == 0 or temp[2] == 0:
            ()
        else:
            permiso_light_list.append([((get_servicio_numbre_list(item))), cvt_light_easier(temp[5]), str(item)])

    # for SUPER 
    for item in sid_list:
        temp = get_super_servicio(item,1)
        if temp[1] == 0:
            ()
        else:
            super_light_list.append(temp)
    return render_template("home.html", send1s=permiso_light_list, send2s=super_light_list, send3s=alineacion_light_list)
   

@app.route("/home")
@login_required
def home_home():
    return redirect('/')

@app.route("/home/rank_permiso")
@login_required
def home_rank_permiso():
    global permiso_light_list, super_light_list, alineacion_light_list
    permiso_light_list = sort_lists(permiso_light_list,1)
    return render_template("home.html", send1s=permiso_light_list, send2s=super_light_list, send3s=alineacion_light_list)

@app.route("/home/rank_super")
@login_required
def home_rank_super():
    global permiso_light_list, super_light_list, alineacion_light_list
    super_light_list = sort_lists(super_light_list,2)
    return render_template("home.html", send1s=permiso_light_list, send2s=super_light_list, send3s=alineacion_light_list)

@app.route("/home/rank_alineacion")
@login_required
def home_rank_alineacion():
    global permiso_light_list, super_light_list, alineacion_light_list
    alineacion_light_list = sort_lists(alineacion_light_list,2)
    return render_template("home.html", send1s=permiso_light_list, send2s=super_light_list, send3s=alineacion_light_list)


@app.route("/home/refresh")
@login_required
def home_refresh():
    refresh_website()
    return redirect('/')

@app.route("/dashboard")
@login_required
def dashboard():
    # all the data of SUPER

    all_lists = get_super_all()
    super_servicio_enrolled = 0 

    for item in sid_list:
        super_servicio_enrolled += (get_super_servicio(item,1))[3]

    etapa_list = []
    acc = 0 
    while acc < len (all_lists):
        etapa_list.append((all_lists[acc])[6])
        acc += 1

    super_permiso_desarrollando = etapa_list.count('Desarrollando')
    super_permiso_terminado = etapa_list.count('Terminado')

    s_all = [super_servicio_enrolled, super_permiso_desarrollando, super_permiso_terminado]

    # all the data of permiso grupo (festoin de proyectos)

    permiso_proyectos_ongoing = find_project_all()[3]
    permiso_ratio_sectorial = find_permit_all(999) ### does this include the ambiental?
    permiso_ratio_dia = (get_env(1))[0]
    permiso_ratio_eia = (get_env(2))[0]

    p_all = [permiso_proyectos_ongoing, permiso_ratio_sectorial, permiso_ratio_dia, permiso_ratio_eia]

    # alineacion
    temp = get_alineacion_all(1)
    aline_servicio_done = temp[1]
    aline_medidas_implementada = temp[2] 
    aline_medidas_not_implementada = temp[3]
    a_all = [aline_servicio_done, aline_medidas_implementada, aline_medidas_not_implementada]
    
    return render_template("dashboard.html", senda=a_all, sends=s_all, sendp=p_all, send_time_now=time_now_nomicro)




@app.route('/alineacion')
@login_required
def alinea_home():
    return render_template("alineacion/home.html", sends=get_alineacion_all(999))


@app.route('/alineacion/servicio/id/search')
@login_required
def alineacion_s_id():
    sid = int(request.args.get('keyword'))
    plist = get_recom_servicio(sid)
    return render_template("alineacion/servicio_result.html", sends=plist)


# maybe can also add the number of companies enrolled so far
@app.route("/super")
@login_required
def get_super_variables():
    all_lists = get_super_all()
    acc = 0 
    
    etapa_list = []
    light_list = []
    enrolled_servicio = 0 

    while acc < len (all_lists):
        etapa_list.append((all_lists[acc])[6])
        light_list.append((all_lists[acc])[7])
        acc += 1 

    planificado = etapa_list.count('Planificado')
    desarrollando = etapa_list.count('Desarrollando')
    terminado = etapa_list.count('Terminado')

    red = light_list.count('Red')
    yellow = light_list.count('Yellow')
    green = light_list.count('Green')
    
    for item in sid_list:
        enrolled_servicio += (get_super_servicio(item,1))[3]
        
    return render_template("super/home.html", send_lists=get_super_all(), send_etapa=[planificado, desarrollando, terminado], send_light=[red, yellow, green], send_enrolled_servicio=enrolled_servicio)


@app.route('/super/servicio/id/search')
@login_required
def super_s_id():
    sid = int(request.args.get('keyword'))
    plist = get_super_servicio(sid, 999)
    return render_template("super/servicio_result.html", sends=plist)


@app.route('/servicio', methods=["GET", "POST"])
@login_required
def servicio_home():
    global all_names_servicios
    inv = []
    servicios_nus = request.form.getlist("check")

    if servicios_nus:
        this_sid_list = servicios_nus
        select_names_servicios = []
    else:
        this_sid_list = sid_list
        all_names_servicios = []

    for item in this_sid_list:
        if inv_block(item) != 0:
            inv.append(inv_block(item))        
            if servicios_nus:
                select_names_servicios.append([get_servicio_numbre_list(item), item])            
            else:
                all_names_servicios.append([get_servicio_numbre_list(item), item])
    
    if not servicios_nus:
            select_names_servicios = all_names_servicios
    
    return render_template("servicio/home.html", send_all_numbre=all_names_servicios, send_select_numbre=select_names_servicios, send_inv=inv)


@app.route('/servicio/check', methods=["GET", "POST"])
@login_required
def servicio_search():
    global servicio_nu, servicio_id

    if request.method == "GET":        
        return render_template("servicio/check.html", send_servicio_numbre_lists=servicio_numbre_list)

    else:
        servicio_nu = request.form.get("servicio_numbre")
        sid = find_servicio_id (servicio_nu)

        plist1 = get_super_servicio(sid, 999)
        plist2 = get_recom_servicio(sid)

        avg_time = []
        ed_num = []
        ing_num = []
        name = []

        for item in pid_list(servicio_id):
            temp = get_gps_data(sid, item)
            if temp[0] == 0 and temp[1] == 0 and temp[2] == 0:
                ()
            else:
                avg_time.append(temp[0])
                ed_num.append(temp[1])
                ing_num.append(temp[2])
                name.append(get_permiso_numbre_list(sid, item))

        else:
            return render_template("servicio/result.html", send1s=plist1, send2s=plist2, send_servicio_numbre_lists=servicio_numbre_list, send_servicio_nu = servicio_nu, send_servicio_id=sid, send_numbre=name, send_avg_time=avg_time, send_ed_num=ed_num, send_ing_num=ing_num)


@app.route("/permiso", methods=["GET", "POST"])
@login_required
def permit_hgain():
    global all_names_servicios
    servicios_nus = request.form.getlist("check")
    avg_time = []
    ed_num = []
    ing_num = []
    ratio = []
    light = [[],[],[],[]]
    
    if servicios_nus:
        this_sid_list = servicios_nus
        select_names_servicios = []
    else:
        this_sid_list = sid_list
        all_names_servicios = []

    for item in this_sid_list:
        temp = get_gps_data(item, 999)
        if temp[0] == 0 or temp[1] == 0 or temp[2] == 0:
            ()
        else:
            avg_time.append(temp[0])
            ed_num.append(temp[1])
            ing_num.append(temp[2])
            ratio.append(temp[5])
            cvt_light(light,(temp[5]))
            if servicios_nus:
                select_names_servicios.append([get_servicio_numbre_list(item), item])            
            else:
                all_names_servicios.append([get_servicio_numbre_list(item), item])
        
    if not servicios_nus:
            select_names_servicios = all_names_servicios

    return render_template("permiso/home.html", send_all_numbre=all_names_servicios, send_select_numbre=select_names_servicios, send_avg_time=avg_time, send_ed_num=ed_num, send_ing_num=ing_num, send_ratio=ratio, send_light=light)


# here is the common function for all the ranking per office 
def get_rank_data(x): 
    global all_names_servicios
    servicios_nus = x

    if servicios_nus:
        this_sid_list = servicios_nus
        select_names_servicios = []
    else:
        this_sid_list = sid_list_no_sea
        all_names_servicios = []

    avg_time = []
    ed_num = []
    ing_num = []
    ratio = []
    illegal_days = []
    inv = []

    # this_sid_list.remove(11) # here i want to exclude SEA (with sid 11) from the ranking here 

    for item in this_sid_list:
        temp = get_gps_data(item, 999)
        if temp[0] == 0 or temp[1] == 0 or temp[2] == 0:
            ()
        else:
            avg_time.append(temp[0])
            ed_num.append(temp[1])
            ing_num.append(temp[2])
            ratio.append(temp[5])
            illegal_days.append(temp[6])
            inv.append(inv_block(item)) 

            if servicios_nus:
                select_names_servicios.append([get_servicio_numbre_list(item), item])            
            else:
                all_names_servicios.append([get_servicio_numbre_list(item), item])
    
    if not servicios_nus:
            select_names_servicios = all_names_servicios

    return ([all_names_servicios, select_names_servicios, avg_time, ed_num, ing_num, ratio, illegal_days, inv])
    #0all names, 1select names, 2avg time, 3finished projects, 4ongiong projects, 5illegal ratio, 6illegal days


@app.route("/permiso/rank_illegal_days", methods=["GET", "POST"])
@login_required
def rank_illegal_days():
    print ("rank_illegal_days")
    checked_servicios = request.form.getlist("check")
    temp = get_rank_data(checked_servicios)
    return render_template("permiso/rank_illegal_days.html", send_all_numbre=temp[0], send_select_numbre=temp[1], send_specific=temp[6])


@app.route("/permiso/rank_permit", methods=["GET", "POST"])
@login_required
def rank_permit():
    print ("rank_permit")
    checked_servicios = request.form.getlist("check")
    temp = get_rank_data(checked_servicios)
    return render_template("permiso/rank_permit.html", send_all_numbre=temp[0], send_select_numbre=temp[1], send_specific=temp[4])


@app.route("/permiso/rank_ratio", methods=["GET", "POST"])
@login_required
def rank_ratio():
    print ("rank_ratio")
    checked_servicios = request.form.getlist("check")
    temp = get_rank_data(checked_servicios)
    return render_template("permiso/rank_ratio.html", send_all_numbre=temp[0], send_select_numbre=temp[1], send_specific=temp[5])


@app.route("/permiso/rank_investment", methods=["GET", "POST"])
@login_required
def rank_investment():
    print ("rank_investment")
    checked_servicios = request.form.getlist("check")
    temp = get_rank_data(checked_servicios)
    return render_template("permiso/rank_investment.html", send_all_numbre=temp[0], send_select_numbre=temp[1], send_specific=temp[7])


@app.route("/permiso/rank_all_factors", methods=["GET", "POST"])
@login_required
def rank_all_factors():
    print ("rank_all_factors")
    checked_servicios = request.form.getlist("check")
    temp = get_rank_data(checked_servicios)
    print (temp)
    return render_template("permiso/rank_all_factors.html", send_all_numbre=temp[0], send_select_numbre=temp[1], send_permit=temp[4],send_ratio=temp[5],send_investment=temp[7],send_illegal_days=temp[6])



@app.route("/permiso/project")
@login_required
def permit_home():
    history_data = find_project_duration(18, 7, year_2dig, month_2dig)
    compare_data = find_project_all()
    
    return render_template("permiso/project.html", send_history_data=history_data, send_compare_data=compare_data)


@app.route("/permiso/permiso", methods=["GET", "POST"])
@login_required
def permit_permiso():
    global servicio_nu, servicio_id
    if request.method == "GET":
        return render_template("permiso/permiso_servicio.html", send_servicio_numbre_lists=servicio_numbre_list)

    # If the method "POST" is used
    else:
        servicio_nu = request.form.get("servicio_numbre")
        servicio_id = find_servicio_id (servicio_nu)
        permiso_numbre_list = get_permiso_numbre_list(servicio_id, 999)
        return render_template("permiso/permiso_servicio_result.html", send_servicio_numbre_lists=servicio_numbre_list, send_servicio_nu=servicio_nu, send_servicio_ids=servicio_id, send_permiso_numbre_lists=permiso_numbre_list)


@app.route("/permiso/permiso/result", methods=["GET", "POST"])
@login_required
def permit_permiso_result():
    global servicio_nu, servicio_id, permiso_nu, permiso_id, permit_dataset

    if request.method == "POST":
        permiso_nu = request.form.get("permiso_numbre")
        permiso_id = find_permiso_id (permiso_nu, servicio_id)
        gps_data = get_gps_data(servicio_id, permiso_id)
        
        avg_time = gps_data[0]
        done_num = gps_data[1]
        ing_num = gps_data[2]
        noinput_num = gps_data[3]
        legal_time = get_legal_data(servicio_id, permiso_id)

        permit_dataset = [avg_time, get_sin_gps(servicio_id,permiso_id)]

        return render_template("permiso/permiso_result.html", send_servicio_numbre_lists=servicio_numbre_list, send_permit_dataset=permit_dataset, send_servicio_nu=servicio_nu, send_servicio_ids=servicio_id, send_permiso_nu=permiso_nu, send_permiso_ids=permiso_id, send_avg_time=avg_time, send_done_num=done_num, get_ing_num=ing_num, send_noinput_num=noinput_num, send_legal_time=legal_time)
    
    else:
        return render_template("permiso/permiso_result.html", send_servicio_numbre_lists=servicio_numbre_list, send_permit_dataset=permit_dataset, send_servicio_nu=servicio_nu, send_servicio_ids=servicio_id, send_permiso_nu=permiso_nu, send_permiso_ids=permiso_id)


@app.route("/permiso/servicio", methods=["GET", "POST"])
@login_required
def permit_servicio():
    global servicio_nu, servicio_id, all_names_permisos

    if request.method == "GET":        
        return render_template("permiso/servicio_servicio.html", send_servicio_numbre_lists=servicio_numbre_list)

    # If the method "POST" is used
    else:
        permiso_nus = request.form.getlist("check")
        
        if (request.form.get("servicio_numbre")):
            servicio_nu = request.form.get("servicio_numbre")
            servicio_id = find_servicio_id (servicio_nu)
            this_pid_list = pid_list(servicio_id)
            all_names_permisos = []
        
        else:
            this_pid_list = permiso_nus
        avg_time = []
        ed_num = []
        ing_num = [] 
        legal_time = []
        legal_ratio = []
        select_names_permisos = []

        for item in this_pid_list:
            temp = get_gps_data(servicio_id, item)
            if temp[0] == 0 and temp[1] == 0 and temp[2] == 0:
                ()
            else:
                avg_time.append(temp[0])
                ed_num.append(temp[1])
                ing_num.append(temp[2])
                legal_time.append(get_legal_data(servicio_id, item))
                legal_ratio.append(round(temp[0]/(get_legal_data(servicio_id, item)),2))

                if permiso_nus:
                    select_names_permisos.append([get_permiso_numbre_list(servicio_id, item),item]) # the names of the permisos that have been selected 
                else:
                    all_names_permisos.append([get_permiso_numbre_list(servicio_id, item),item]) # all the name of the permisos of that servicio 
        
        if not permiso_nus:
            select_names_permisos = all_names_permisos
        return render_template("permiso/servicio_result.html", send_servicio_numbre_lists=servicio_numbre_list, send_servicio_nu=servicio_nu, send_servicio_id=servicio_id, send_all_numbre=all_names_permisos, send_select_numbre=select_names_permisos, send_avg_time=avg_time, send_ed_num=ed_num, send_ing_num=ing_num, send_legal_time=legal_time, send_legal_ratio=legal_ratio)


@app.route('/permiso/servicio/numbre/search')
@login_required
def permit_s_numbre():
    global all_names_permisos
    servicio_nu = str(request.args.get('keyword'))
    servicio_id = find_servicio_id(servicio_nu)


    avg_time = []
    ed_num = []
    ing_num = []
    select_names_permisos = []
    legal_time = []
    legal_ratio = []
    
    for item in pid_list(servicio_id):
        temp = get_gps_data(servicio_id, item)
        if temp[0] == 0 and temp[1] == 0 and temp[2] == 0:
            ()
        else:
            avg_time.append(temp[0])
            ed_num.append(temp[1])
            ing_num.append(temp[2])
            select_names_permisos.append([get_permiso_numbre_list(servicio_id, item),item])
            legal_time.append(get_legal_data(servicio_id, item))
            legal_ratio.append(round(temp[0]/(get_legal_data(servicio_id, item)),2))

    else:
        all_names_permisos = select_names_permisos
        return render_template("permiso/servicio_result.html", send_servicio_numbre_lists=servicio_numbre_list, send_servicio_nu=servicio_nu, send_servicio_id=servicio_id, send_all_numbre=all_names_permisos, send_select_numbre=select_names_permisos, send_avg_time=avg_time, send_ed_num=ed_num, send_ing_num=ing_num, send_legal_time=legal_time, send_legal_ratio=legal_ratio)



@app.route('/permiso/permiso/numbre/search')
@login_required
def permit_p_numbre():
    keyword = (request.args.get('keyword'))
    permiso_nu = (seperate(keyword))[1]
    servicio_id = (seperate(keyword))[0]
    servicio_nu = get_servicio_numbre_list(servicio_id)
    permiso_id = find_permiso_id(permiso_nu, servicio_id)

    gps_data = get_gps_data(1, permiso_id)
    avg_time = gps_data[0]
    done_num = gps_data[1]
    ing_num = gps_data[2]
    noinput_num = gps_data[3]
    legal_time = get_legal_data(1, permiso_id) ### i think there is a big problem here 
    permit_dataset = [avg_time, get_sin_gps(servicio_id,permiso_id)]
    if get_sin_gps(servicio_id,permiso_id) == 0:
        saved_time = 0
    else:
        saved_time = round(100*(get_sin_gps(servicio_id,permiso_id) - avg_time) / (get_sin_gps(servicio_id,permiso_id)))

    return render_template("permiso/permiso_result.html", send_servicio_numbre_lists=servicio_numbre_list, send_permit_dataset=permit_dataset, send_servicio_nu=servicio_nu, send_servicio_ids=servicio_id, send_permiso_nu=permiso_nu, send_permiso_ids=permiso_id, send_avg_time=avg_time, send_done_num=done_num, get_ing_num=ing_num, send_noinput_num=noinput_num, send_legal_time=legal_time, send_saved_time=saved_time)


@app.route("/permiso/per_month", methods=["GET", "POST"])
@login_required
def permit_per_month():
    history_data = find_permit_duration(18, 7, year_2dig, month_2dig) # this gives the data for each
    return render_template("permiso/per_month.html", send_history_data=history_data)

@app.route("/permiso/per_office", methods=["GET", "POST"])
@login_required
def permit_per_office():
    avg_time = []
    ed_num = []
    ing_num = []
    name = []
    ratio = []
    for item in sid_list:
        temp = get_gps_data(item, 999)
        if temp[0] == 0 or temp[1] == 0 or temp[2] == 0:
            ()
        else:
            avg_time.append(temp[0])
            ed_num.append(temp[1])
            ing_num.append(temp[2])
            name.append(get_servicio_numbre_list(item))
            ratio.append(temp[5])
    else:
        return render_template("permiso/per_office.html", send_numbre=name, send_avg_time=avg_time, send_ed_num=ed_num, send_ing_num=ing_num, send_ratio = ratio)



@app.route("/permiso/permit", methods=["GET", "POST"])
@login_required
def permit_permit():

    if request.method == "GET":
        return render_template("permiso/permit.html")

    else:
        # Collect the info the "POST" html
        ID = request.form.get("permit_check_id")
        permit_check_id_avg = permit_avg(ID)
        return render_template("permiso/result.html", data_package=permit_check_id_avg)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0')

