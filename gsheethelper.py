import gspread
import datetime 
from statistics import mean, median, stdev 
from oauth2client.service_account import ServiceAccountCredentials
from sqlhelper import get_all_servicio,get_all_permiso

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('**********', scope)
client = gspread.authorize(creds)

program_start_time= datetime.datetime.now()
counter1 = 0
counter2 = 0

def reconnect():
    global program_start_time, counter1, counter2, scope, creds, client 
    if not (datetime.datetime.now() > program_start_time + datetime.timedelta(minutes=2)):
        # print ("Google Sheet ok"+str(counter1))
        counter1 += 1 
    else:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('**********', scope)
        client = gspread.authorize(creds)
        print ("Google sheet Reconnect"+str(counter2))
        program_start_time = datetime.datetime.now() #Resets the Program Start Time
        counter2 += 2 


# declaring some global variables 
super_global_list = []
super_rows = 0

recom_global_list = []
recom_rows = 0


# this search the database of those permits that are not done by GPS, and find their average processing time
# p = 999 means all of the permits for oficina with servicio_id = s
# p = any other number, for example 4, means the permit with servicio_id = s and permiso_id = 4

def get_sin_gps(s,p):
    reconnect()
    sheet = client.open("gps_data").worksheet('copy_sin')

    list0 = sheet.col_values(2) # servicio id
    list1 = sheet.col_values(4) # permiso id
    list2 = sheet.col_values(8) # the time 
    time_list = []
    acc = 1 

    if p == 999:
        while acc < len(list0):    
            if int(list0[acc]) == s:
                time_list.append(int(list2[acc]))
                acc += 1 
            else:
                acc += 1 
    else:
        while acc < len(list0):   
            if int(list0[acc]) == s and int(list1[acc]) == p:
                    time_list.append(int(list2[acc]))
                    acc += 1 
            else:
                acc += 1 

    if time_list:
        return (round(mean(time_list)))
    else:    
        return 0
        


def get_recom_all():
    global recom_global_list, recom_rows
    reconnect()
    sheet = client.open("gps_data").worksheet('recomtest')

    list0 = sheet.col_values(1) # servicio id
    list1 = sheet.col_values(2) # proyecto id
    list2 = sheet.col_values(4) # servicio/oficina id
    list3 = sheet.col_values(6) # details de recommendacion
    list4 = sheet.col_values(8) # etapa - desarrolando 
    list5 = sheet.col_values(9) # light - red 

    all_list = []
    acc = 2 

    while acc < len(list1):
        all_list.append([list0[acc], list1[acc], list2[acc], list3[acc],list4[acc],list5[acc]])
        acc += 1
    else:
        recom_global_list = all_list
        recom_rows = len(list0)
        return(all_list)


def get_recom_servicio(s):
    global recom_global_list, recom_rows
    reconnect()
    if recom_global_list == []:
        get_recom_all()
    else:
        ()

    all_list = []
    acc = 0

    while int((recom_global_list[acc])[0]) != s:
        if (acc+1) == (recom_rows-2):
            return(s,0)
        else:
            acc += 1
        
    else:
        while int((recom_global_list[acc])[0]) == s:
            all_list.append(recom_global_list[acc])
            if (acc+1) == (recom_rows-2):
                return(all_list)
            else:
                acc += 1
        else:
            return(all_list)

def get_recom_ratio(s):
    global recom_global_list, recom_rows
    reconnect()
    if recom_global_list == []:
        get_recom_all()
    else:
        ()

    etapa_list = []
    acc = 0

    while int((recom_global_list[acc])[0]) != s:
        if (acc+1) == (recom_rows-2):
            return(0,0)
        else:
            acc += 1
        
    else:
        while int((recom_global_list[acc])[0]) == s:
            etapa_list.append((recom_global_list[acc])[4])
            if (acc+1) == (recom_rows-2):
                return(etapa_list.count("Implementada"),len(etapa_list))
            else:
                acc += 1
        else:
            return(etapa_list.count("Implementada"),len(etapa_list))


def get_alineacion_all(x): 
    reconnect()
    sheet = client.open("gps_data").worksheet('alinea')
    sheet_lists = sheet.get_all_values()

    all_list = []
    acc = 2 

    number_medida_implementada = 0
    number_medidas_not_implementada = 0

    if x == 999: #get all the details information
        while acc < len(sheet_lists):
            (sheet_lists[acc]).append(str(get_recom_ratio(int((sheet_lists[acc])[0]))[0])+"/"+str(get_recom_ratio(int((sheet_lists[acc])[0]))[1]))
            all_list.append(sheet_lists[acc])
            acc += 1
        else:
            return(all_list)
    else: # x == 1: just for one line
        number_alineada = 0
        while acc < len(sheet_lists): #get only one line
            e = sheet_lists[acc]
            if e[7] == "Y":
                temp = get_recom_ratio(int((sheet_lists[acc])[0]))
                all_list.append([e[0], e[2], e[8], e[7],str(temp[0])+"/"+str(temp[1])]) ### here is where I was editing 
                number_alineada += 1
                number_medida_implementada += temp[0]
                number_medidas_not_implementada += (temp[1]-temp[0])
            else:
                all_list.append([e[0], e[2], e[8], e[7],""])
            acc += 1
        else:
            return(all_list, number_alineada, number_medida_implementada, number_medidas_not_implementada)



def get_super_all():
    global super_global_list, super_rows
    reconnect()
    sheet = client.open("gps_data").worksheet('supertest')
    sheet_lists = sheet.get_all_values()

    all_list = []
    acc = 1 

    while acc < len(sheet_lists):
        all_list.append(sheet_lists[acc])
        acc += 1
    else:
        super_global_list = all_list
        super_rows = len(sheet_lists)
        return(all_list)



def get_super_servicio(s,p):
    global super_global_list, super_rows
    reconnect()
    if super_global_list == []:
        get_super_all()
    else:
        ()

    all_list = []
    acc = 0

    if p == 999: #get all the record in that servicio id
        while int((super_global_list[acc])[0]) != s:
            if (acc+1) == (super_rows-1):
                return(s,0)
            else:
                acc += 1
            
        else:
            while int((super_global_list[acc])[0]) == s:
                all_list.append(super_global_list[acc])
                if (acc+1) == (super_rows-1):
                    return(all_list)
                else:
                    acc += 1
            else:
                return(all_list)

    else: #get the macro condition of one servicio organizicion, giving out only 1 output 

        while int((super_global_list[acc])[0]) != s:
            if (acc+1) == (super_rows-1):
                return(s,0,0,0)
            else:
                acc += 1
        else:
            light_list = []
            etapa_list = []
            while int((super_global_list[acc])[0]) == s:
                light_list.append((super_global_list[acc])[7])
                etapa_list.append((super_global_list[acc])[6])
                if (acc+1) == (super_rows-1):
                    return(s,0,0,0)
                else:
                    acc += 1
            else:
                def final_light():
                    if 'Red' in light_list:
                        return('Red')
                    elif 'Yellow' in light_list:
                        return('Yellow')
                    else:
                        return('Green')
                def if_any_terminado(): # whether there is any that has terminated 
                    if etapa_list.count('Terminado') != 0:
                        return (1)
                    else:
                        return (0)
                ratio = (str(etapa_list.count("Terminado"))+"/"+str(len(etapa_list))) # ratio between the terminado and the rest of the permits
                
        return([(super_global_list[acc-1])[0], (super_global_list[acc-1])[2], final_light(), if_any_terminado(),ratio]) # return the servicio id, servicio numbre, final light, and if one completed
        # if p = 1, then "['1', 'BBNN', 'Red', 1, '2/8']"
        # if p = 999, then  it will be every permits that SUPER have 


def update_list(sheet,input_list):    
    reconnect()
    for row in range(len(input_list)):
        for column in range(len(input_list[0])):
            sheet.update_cell((row+2), (column+1), (input_list[row])[column])

def update_servicio_list():
    reconnect()
    sheet = client.open("gps_data").worksheet('servicio_updated')
    input_list = get_all_servicio()
    update_list(sheet,input_list)

def update_permiso_list():
    reconnect()
    sheet = client.open("gps_data").worksheet('permiso_updated')
    input_list = get_all_permiso()
    update_list(sheet,input_list)


