from statistics import mean, median, stdev 
import pymssql, datetime

# have the access to the database using our own configuration
conn = pymssql.connect(('**********')
cursor = conn.cursor()
counter1 = 0 
counter2 = 0

time_now = datetime.datetime.now()
time_now_nomicro = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
year_2dig = int((str(time_now.year))[2:4])
month_2dig = time_now.month

program_start_time= datetime.datetime.now()

def reconnect():
    global program_start_time, counter1, counter2, cursor, conn
    if not (datetime.datetime.now() > program_start_time + datetime.timedelta(minutes=2)):
        # print ("SQL Server ok"+str(counter1))
        counter1 += 1 
    else:
        conn = pymssql.connect('**********')
        cursor = conn.cursor()
        print ("SQL Server Reconnect"+str(counter2))
        program_start_time = datetime.datetime.now() #Resets the Program Start Time
        counter2 += 1 

def seperate(x):
    i = 0
    a = ""
    while x[i] != "_":
        a = a + (x[i])
        i+=1
    else:
        return (int(a), x[i+1:len(x)])
    
def cvt_light(lis,x):
    (r,y,g,w) = lis
    if x > 300:
        r.append(1)
        y.append(0)
        g.append(0)
        w.append(0)
    elif x>150:
        r.append(0)
        y.append(1)
        g.append(0)
        w.append(0)
    else:
        r.append(0)
        y.append(0)
        g.append(1)
        w.append(0) 
    return ((r,y,g,w))


def cvt_light_easier(x):
    if x > 300:
        return "Red"
    elif x>150:
        return "Yellow"
    else:
        return "Green"

# find the duration between 2 datetime files, a is older, b is younger
def duration_days(a, b): 
    return int(((a-b).days)*5/7)
    

def get_max_sid():
    cursor.execute("SELECT ServicioId FROM ServicioPermisos")
    sid_list = []
    for row in cursor:
        sid_list.append(row[0])
    return (max(sid_list))


def permit_avg (x):
    reconnect()
    # get the data 
    cursor.execute("SELECT ProyectoGestionPermisosFechaIn, ProyectoGestionPermisosFechaOb, STServicioPermisoid FROM ProyectoGestionPermisos WHERE STServicioPermisoid = (%s)", x)

    newlist = []
    # run the recursion to add the number of days of the permission to the list 
    for row in cursor:
        duration = duration_days (row[1], row[0])
        if duration < 0 :
            newlist 
        else: 
            newlist.append (duration)

    return (round(mean(newlist)))

def get_legal_data (s, p):
    reconnect()
    cursor.execute("SELECT PermisoPlazo FROM ServicioPermisos WHERE ServicioId = (%s) AND PermisoId = (%d)", (s, p))
    for row in cursor:
        if (row[0]) == '':
            return 120
        else:
            return (int(''.join([n for n in (row[0]) if n.isdigit()])))

def fix_legal (x):
    if (x[2]) == '':
        return 120
    else:
        return (int(''.join([n for n in (x[2]) if n.isdigit()])))


def find_permit_month (yy, mm):
    reconnect()
    if mm == 12:
        cursor.execute("""SELECT [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaIn] AS [ProyectoGestionPermisosFechaIn],
        [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] AS [ProyectoGestionPermisosFechaOb],
        [ServicioPermisos].[PermisoPlazo] AS [PermisoPlazo]
        FROM [dbo].[ProyectoGestionPermisos] [ProyectoGestionPermisos]
        INNER JOIN [dbo].[ServicioPermisos] [ServicioPermisos] ON (([ProyectoGestionPermisos].[STServicioServicioid] = [ServicioPermisos].[ServicioId]) AND ([ProyectoGestionPermisos].[STServicioPermisoid] = [ServicioPermisos].[PermisoId])) WHERE [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] >= '20"""+str(yy)+"-"+str(mm)+"-1 00：00：00' AND [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] < '20"+str(yy+1)+"-"+str(1)+"-1 00：00：00'")
    else:
        cursor.execute("""SELECT [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaIn] AS [ProyectoGestionPermisosFechaIn],
        [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] AS [ProyectoGestionPermisosFechaOb],
        [ServicioPermisos].[PermisoPlazo] AS [PermisoPlazo]
        FROM [dbo].[ProyectoGestionPermisos] [ProyectoGestionPermisos]
        INNER JOIN [dbo].[ServicioPermisos] [ServicioPermisos] ON (([ProyectoGestionPermisos].[STServicioServicioid] = [ServicioPermisos].[ServicioId]) AND ([ProyectoGestionPermisos].[STServicioPermisoid] = [ServicioPermisos].[PermisoId])) WHERE [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] >= '20"""+str(yy)+"-"+str(mm)+"-1 00：00：00' AND [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] < '20"+str(yy)+"-"+str(mm+1)+"-1 00：00：00'")
  
    acc = [] 
    num = 0 
    legal_ratio = []

    for row in cursor:
        if (row[0]).year > 2000:
            acc.append(duration_days(row[1], row[0]))   
            num += 1 
            legal_time = fix_legal(row)
            legal_ratio.append(100*(duration_days(row[1], row[0]))/legal_time)
        else:
            ()

    if acc == []:
        return (0, 0, 0)
    else:
        return ((round(mean(acc))), num, (round(mean(legal_ratio), 2))) # return the avergage time of that permit, their number, and the ratio


def find_permit_duration (y1, m1, y2, m2): # this is for the monthly graph 
    ycount = y1
    avg_data = []
    num_data = []
    label = [] # here is the label of the month, like 18-8
    ratio = []
    while ycount < y2: # when they have different starting year, like 2018, 2019
        if (y2 - y1) == 1:
            mcount = m1
        else:
            mcount = 1

        while mcount <= 12:
            temp = find_permit_month(ycount, mcount)
            avg_data.append(temp[0])
            num_data.append(temp[1])
            label.append(str(ycount) + "-" + str(mcount))
            ratio.append(temp[2])
            mcount += 1 
        else:
            ycount += 1             

    else:
        if (y2 - y1) > 0:
            mcount = 1
        else:
            mcount = m1
        while mcount <= m2:
            temp = find_permit_month(ycount, mcount)
            avg_data.append(temp[0])
            num_data.append(temp[1]) 
            label.append(str(ycount) + "-" + str(mcount))
            ratio.append(temp[2])
            mcount += 1 
        else:
            return (label, num_data, avg_data, ratio)   

def find_permit_all(s):
    reconnect()

    cursor.execute("""SELECT [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaIn] AS [ProyectoGestionPermisosFechaIn],
    [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] AS [ProyectoGestionPermisosFechaOb],
    [ServicioPermisos].[PermisoPlazo] AS [PermisoPlazo]
    FROM [dbo].[ProyectoGestionPermisos] [ProyectoGestionPermisos]
    INNER JOIN [dbo].[ServicioPermisos] [ServicioPermisos] ON (([ProyectoGestionPermisos].[STServicioServicioid] = [ServicioPermisos].[ServicioId]) AND ([ProyectoGestionPermisos].[STServicioPermisoid] = [ServicioPermisos].[PermisoId])) WHERE [ProyectoGestionPermisos].[STServicioServicioid] != 11 AND [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] >= '2010-1-1 00：00：00' AND [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] < '""" + str(time_now_nomicro)+"'")

    ratio = []
    for row in cursor:
        ratio.append((duration_days(row[1], row[0]))/(fix_legal(row)))
    else:
        return (round(100*mean(ratio)))
 

def find_project_month (yy, mm):
    reconnect()
    if mm == 12:
        cursor.execute("SELECT ProyectoFechaIncorporacionCAEN, ProyectoFechaInicioOperacion, ProyectoInversionTotal FROM Proyecto WHERE ProyectoFechaInicioOperacion >= '20"+str(yy)+"-"+str(mm)+"-1 00：00：00' AND ProyectoFechaInicioOperacion < '20"+str(yy+1)+"-"+str(1)+"-1 00：00：00' AND MacroProcesoId = 5")
    else:
        cursor.execute("SELECT ProyectoFechaIncorporacionCAEN, ProyectoFechaInicioOperacion, ProyectoInversionTotal FROM Proyecto WHERE ProyectoFechaInicioOperacion >= '20"+str(yy)+"-"+str(mm)+"-1 00：00：00' AND ProyectoFechaInicioOperacion < '20"+str(yy)+"-"+str(mm+1)+"-1 00：00：00'AND MacroProcesoId = 5")

    num = 0 # number of projects 
    inv = 0 # number of investment

    for row in cursor:
        num += 1  
        if row[2]:
            inv += row[2]
        else:
            inv += 0

    if num == 0:
        return (0, 0)
    else:
        return (num, int(inv))
 

def find_project_duration (y1, m1, y2, m2): # this is for the monthly graph 
    ycount = y1
    num_data = [] # how many we have that month
    label = []
    inv = []
    while ycount < y2: # when they have different starting year, like 2018, 2019
        if (y2 - y1) == 1:
            mcount = m1
        else:
            mcount = 1

        while mcount <= 12:
            temp = find_project_month(ycount, mcount)
            num_data.append(temp[0])
            label.append(str(ycount) + "-" + str(mcount))
            inv.append (temp[1])
            mcount += 1 
        else:
            ycount += 1             

    else:
        if (y2 - y1) > 0:
            mcount = 1
        else:
            mcount = m1
        while mcount <= m2:
            temp = find_project_month(ycount, mcount)
            num_data.append(temp[0]) 
            label.append(str(ycount) + "-" + str(mcount))
            inv.append (temp[1])
            mcount += 1 
        else:
            return (label, num_data, inv)   


def find_project_all (): # including the projects in the future, those ongoing projects
    reconnect()
    inv_ed = sum((find_project_duration(18, 7, year_2dig, month_2dig))[2])
    num_ed = sum((find_project_duration(18, 7, year_2dig, month_2dig))[1])

    cursor.execute("SELECT ProyectoFechaIncorporacionCAEN, ProyectoFechaInicioOperacion, ProyectoInversionTotal FROM Proyecto WHERE ProyectoPublicacionTableau = 'TRUE'")

    inv_ing = 0 
    num_ing = 0 # how many are going on right now

    for row in cursor:
        num_ing += 1
        if row[2]:
            inv_ing += row[2]
        else:
            inv_ing += 0
    return(inv_ed, num_ed, int(inv_ing), num_ing)


def get_env(pp):
    reconnect()
    def env_package(x):
        if x == 999:
            return (0, "11")
        elif x == 1:
            return ("DIA","1")
        else: # means the case of "EIA" as the input 2 
            return ("EIA", "2")

    if pp == 999:
        cursor.execute("SELECT ProyectoFechaIngresoSEIA, ProyectoFechaResolSEIA, TipoIngreso FROM Proyecto WHERE ProyectoFechaIngresoSEIA IS NOT NULL")
    else: # for DIA, legal time 120 days
        cursor.execute("SELECT ProyectoFechaIngresoSEIA, ProyectoFechaResolSEIA, TipoIngreso FROM Proyecto WHERE ProyectoFechaIngresoSEIA IS NOT NULL AND TipoIngreso = (%s)", (env_package(pp))[0])

    n_time = 0
    time_list = []
    ratio_list = []
    over_days = 0

    def env_legal (x):
        if x[2] == "DIA":
            return 120
        else:
            return 180

    for row in cursor:
        if row[1]: 
            if (row[1]) > datetime.datetime.strptime('2019-03-01 00:00:00', '%Y-%m-%d %H:%M:%S'):
                duration = duration_days(row[1], row[0])
                time_list.append(duration)
                ratio_list.append(duration/(env_legal(row)))
                if duration > env_legal(row):
                    over_days += (duration - env_legal(row))
            else:
                ()
        else:
            n_time += 1

    return (round(mean(time_list)), len(time_list), n_time, 0, (env_package(pp))[1], round(100*mean(ratio_list)),round(over_days/len(time_list))) # return me how many projects have been given after the time, and their average
        # gives out the 0-average time, 1-how many permisos, 2-the not finished permisos, 3-don't have starting date data, 4-the permisoid, 5-ratio to the legal time, 6-average overtime days


def get_gps_data (s, p):
    reconnect()
    # gives out the average time, how many projects, the not finished projects, don't have starting date data, name, ratio to the legal time 

    if s == 11:
        return(get_env(p))

    else:
        if p == 999:
            cursor.execute("""SELECT [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaIn] AS [ProyectoGestionPermisosFechaIn],
            [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] AS [ProyectoGestionPermisosFechaOb],
            [ServicioPermisos].[PermisoPlazo] AS [PermisoPlazo]
            FROM [dbo].[ProyectoGestionPermisos] [ProyectoGestionPermisos]
            INNER JOIN [dbo].[ServicioPermisos] [ServicioPermisos] ON (([ProyectoGestionPermisos].[STServicioServicioid] = [ServicioPermisos].[ServicioId]) AND ([ProyectoGestionPermisos].[STServicioPermisoid] = [ServicioPermisos].[PermisoId])) WHERE [ProyectoGestionPermisos].[STServicioServicioid] =""" + str(s))
        
        else: 
            cursor.execute("""SELECT [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaIn] AS [ProyectoGestionPermisosFechaIn],
            [ProyectoGestionPermisos].[ProyectoGestionPermisosFechaOb] AS [ProyectoGestionPermisosFechaOb],
            [ServicioPermisos].[PermisoPlazo] AS [PermisoPlazo]
            FROM [dbo].[ProyectoGestionPermisos] [ProyectoGestionPermisos]
            INNER JOIN [dbo].[ServicioPermisos] [ServicioPermisos] ON (([ProyectoGestionPermisos].[STServicioServicioid] = [ServicioPermisos].[ServicioId]) AND ([ProyectoGestionPermisos].[STServicioPermisoid] = [ServicioPermisos].[PermisoId])) WHERE [ProyectoGestionPermisos].[STServicioServicioid] =""" + str(s) +  "AND [ProyectoGestionPermisos].[STServicioPermisoid] =" + str (p))

        y_time = [] # the finished project times 
        ratio = [] 
        n_num = 0 #the number of permits that are not finished 
        u_num = 0 #the number of permits that don't have starting date data 
        over_days = 0

        for row in cursor:
            duration = duration_days(row[1], row[0])
            if (row[0]).year < 2010 :
                u_num += 1
            elif duration < 0: # this means this projects are still going on, not finished 
                n_num += 1 
            else: # this means this project is finished 
                y_time.append (duration)
                ratio.append (duration/fix_legal(row))
                if duration > fix_legal(row):
                    over_days += (duration - fix_legal(row))
            
        if p == 999:
            name = (str(s))
        else:
            name = (str(p))

        if y_time:
            return (round(mean(y_time)), len(y_time), n_num, u_num, name, round(100*mean(ratio)), round(over_days/(len(y_time)))) # send out all the data 
            # gives out the 0-average time, 1-how many permisos, 2-the not finished permisos, 3-don't have starting date data, 4-the permisoid, 5-ratio to the legal time, 6-average overtime days
        
        else: # which means there are no finished projects in this servicio
            return (0, 0, n_num, u_num, name, 0)



def inv_block(s): #input the id the servicio, and see how much investment is blocked 
    reconnect()
    cursor.execute("""SELECT DISTINCT [ProyectoGestionPermisos].[ProyectoId] AS [ProyectoId],
    [Proyecto].[ProyectoInversionTotal] AS [Inversion]
    FROM [dbo].[ProyectoGestionPermisos] [ProyectoGestionPermisos]
    INNER JOIN [dbo].[Proyecto] [Proyecto] ON ([ProyectoGestionPermisos].[ProyectoId] = [Proyecto].[ProyectoId])
    WHERE STServicioServicioId = (%s)""", s)

    inv_sum = 0
    for row in cursor:
        if row[1]:
            inv_sum += int(row[1])
        else:
            inv_sum += 0 # this is when the estimate inversion is NULL
    return (inv_sum)


def get_servicio_numbre_list (x):
    reconnect()
    if x == 999:
        cursor.execute("SELECT ServicioNombre FROM Servicio")
    else:
        cursor.execute("SELECT ServicioNombre FROM Servicio WHERE ServicioId = (%s)", x)
    snlist = []
    
    if cursor.rowcount == 0:
        return ['Sin Numbre']
    else:
        for row in cursor:
            snlist.append ((row)[0])
        if x == 999:
            return snlist
        else:
            if x == 999:
                return snlist
            else:
                return snlist[0]


def find_servicio_id (x):
    reconnect()
    cursor.execute("SELECT ServicioId FROM Servicio WHERE ServicioNombre = (%s)", x)
    silist = []
    for row in cursor:
        silist.append (row)
    return (silist[0])[0]


def get_permiso_numbre_list (s, p):
    reconnect()
    if s == 11:
        if p == 999:
            return (["DIA", "EIA"])
        elif p == 1:
            return ("DIA")
        else:
            return ("EIA")
    else:
        if p == 999:
            cursor.execute("SELECT PermisoNombre FROM ServicioPermisos WHERE ServicioId = (%s)", s)
        else:
            cursor.execute("SELECT PermisoNombre FROM ServicioPermisos WHERE ServicioId = (%s) AND PermisoId = (%d)", (s, p))

        pnlist = []

        if cursor.rowcount == 0:
            return ['Sin Numbre']
        else:
            for row in cursor:
                pnlist.append (row[0])

            if p == 999:
                return pnlist
            else:
                return pnlist[0]

def find_permiso_id (pn, si):
    reconnect()
    if si == 11:
        if pn == 'DIA':
            return 1
        else:
            return 2
    else:
        cursor.execute("SELECT PermisoId FROM ServicioPermisos WHERE PermisoNombre = (%s) AND ServicioId = (%d)", (pn, si))
        pilist = []
        for row in cursor:
            pilist.append (row)

        if pilist == []:
            return 777 # 777 means the permiso id doesn't exist
        else:
            return ((pilist)[0])[0]

def get_all_servicio():
    reconnect()
    cursor.execute("SELECT ServicioId, ServicioNombre FROM Servicio")
    servicio_list = []
    for row in cursor:
        servicio_list.append(row)
    return (servicio_list)

def get_all_permiso():
    reconnect()
    cursor.execute("""SELECT [ServicioPermisos].[ServicioId] AS [ServicioId],
        [ServicioPermisos].[PermisoId] AS [PermisoId],
        [Servicio].[ServicioNombre] AS [ServicioNombre],
        [ServicioPermisos].[PermisoNombre] AS [PermisoNombre]
        FROM [dbo].[Servicio] [Servicio]
        INNER JOIN [dbo].[ServicioPermisos] [ServicioPermisos] ON ([Servicio].[ServicioId] = [ServicioPermisos].[ServicioId])""")
    permiso_list = []
    for row in cursor:
        permiso_list.append(row)
    return (permiso_list)

