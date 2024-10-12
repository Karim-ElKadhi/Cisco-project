import paramiko
import re
from flask import Flask, jsonify, request, render_template
import time
from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_session import Session


import psycopg2
app = Flask(__name__)
app.secret_key = 'admin'

#connexion avec la bd
def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database='cisco_test',
        user='karim',
        password='123456'
    )
    return connection
#insertion des ports
def insert_prt(switch_n):
    connection = get_db_connection()
    cursor = connection.cursor()
    for port_number in range(1, 49):
            cursor.execute(
                'INSERT INTO ports (switch_n, port, locked) VALUES (%s, %s, %s)',
                (switch_n, str(port_number), 'no')
            )
        
    connection.commit()
    cursor.close()
    connection.close()
#recuperer les vlans
def get_vlans():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT nom, port ,type FROM vlan')
    vlans = cursor.fetchall()
    cursor.close()
    connection.close()
    return vlans
#recuperer les switchs
def get_switchs():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT switch_name, switch_number FROM switch')
    switchs = cursor.fetchall()
    cursor.close()
    connection.close()
    return switchs
'''app.config['SECRET_KEY'] = 'admin'
app.config['SESSION_TYPE'] = 'filesystem'  
Session(app)
'''
#recuperer les ports
def get_ports():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT switch_n,port,locked FROM ports GROUP BY switch_n,port,locked ORDER BY port ASC;')
    ports = [(row[0], int(row[1]), row[2]) for row in cursor.fetchall()]
    ports.sort(key=lambda x: x[1]) 
    cursor.close()
    connection.close()
    return ports
#recuperer le type 
def get_type(nom):
    vlans=get_vlans()
    for vlan in vlans:
        if nom==vlan[1]:
            type=vlan[2]
    return type        

#page principale

@app.route('/', methods=['GET', 'POST'])

def show_switchs():
    switchs=get_switchs()
    return render_template('switch.html',switchs=switchs)

#dashboard
@app.route('/dashboard', methods=['GET', 'POST'])


def show_file_content():
    content = ""
    current_vlan = ""
    action= ""
    vlans=get_vlans()

    switch_number = request.form.get('switch_number', '')
    port_number = request.form.get('port_number', '')
    action = request.form.get('action', 'show_config')
    if switch_number and port_number:
        content, current_vlan = fetch_config_from_device(switch_number, port_number)
        
    if request.method == 'POST':
        switch_number = request.form.get('switch_number', '')
        port_number = request.form.get('port_number', '')
        action = request.form.get('action','show_config')

        if action == 'show_config':
            content,current_vlan = fetch_config_from_device(switch_number, port_number)
            if not content:
                content = "Unable to retrieve configuration or make changes."

              

        elif action == 'change_vlan':
            
            #current_vlan = request.form.get('current_vlan', '')
            new_vlan = request.form.get('vlanNumber', '')
            type=get_type(new_vlan)
            new_vlan_text = request.form.get('new_vlan_text', '')
            if current_vlan and new_vlan:
                content = change_vlan(switch_number, port_number, current_vlan, new_vlan,new_vlan_text,type)
                content, current_vlan = fetch_config_from_device(switch_number, port_number)

            else:
                content = "Both Current VLAN and New VLAN are required for VLAN changes."

    
    
    return render_template('test.html', file_content=content ,current_vlan=current_vlan,action=action,vlans=vlans)
#recuperation de la config cisco

def fetch_config_from_device(switch_number, port_number):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('10.255.25.2', username='root', password='ANS#150')
        channel = client.invoke_shell()
        
        command = f'show running-config interface GigabitEthernet{switch_number}/0/{port_number}\n'
        channel.send(command)
        time.sleep(0.5)  
       
    # Receive output
        output = collect_output(channel.recv(65535).decode('utf-8'))
        

        channel.close()
        client.close()

        vlan_match = re.search(r'switchport access vlan (\d+)', output)
        vlan_trunk = re.search(r'switchport trunk allowed (.+)', output)

        vlan_number = "Access"+vlan_match.group(1) if vlan_match else "Trunk "+vlan_trunk.group(1) 


        return output,vlan_number
    except Exception as e:
        print(f"Error connecting to device: {e}")
        return None

def collect_output(output):
        start_idx = output.find('!')
        end_idx = output.find("end", start_idx)
    
        if start_idx != -1 and end_idx != -1:
            return output[start_idx+1:end_idx + len("end")].strip()


def parse_vlan_name(vlan_full_name):
 
    match = re.match(r"(access|trunk)\s+(\d+(?:-\d+)?)", vlan_full_name,re.IGNORECASE)
    if match:
        return match.group(0).capitalize(), match.group(2)
    return None, None



def parse_switch_name(switch_full_name):
 
    match = re.match(r"(switch)\s*(\d+)", switch_full_name, re.IGNORECASE)
    if match:
        return match.group(0), match.group(2)
    return None, None
#ajout des vlans
def add_vlan_to_database(vlan_name, vlan_port):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO vlan (nom, port) VALUES (%s, %s)", (vlan_name, vlan_port))
    conn.commit()
    cur.close()
    conn.close() 

#changement de vlans
def change_vlan(switch_number, port_number, current_vlan, new_vlan,new_vlan_text,type):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('10.255.25.2', username='root', password='ANS#150')
        channel = client.invoke_shell()


       

        
        channel.send(f'conf t \n')
        time.sleep(0.2)
        channel.send(f'interface GigabitEthernet{switch_number}/0/{port_number} \n')
        if type=="Trunk"  :
            # Specific commands for trunk
            #channel.send(f'no switchport mode access \n')
            channel.send(f'switchport mode Trunk \n')
            channel.send(f'no switchport access vlan \n')
            time.sleep(0.3)
            channel.send(f'switchport trunk allowed vlan {new_vlan} \n')
            channel.send(f'description {new_vlan_text} \n')
            time.sleep(0.2)
            channel.send('end \n')
            time.sleep(0.2)
            channel.send(f'show running-config interface GigabitEthernet{switch_number}/0/{port_number} \n')
            time.sleep(0.1)
            output = collect_output(channel.recv(65535).decode('utf-8'))
            channel.close()
            client.close()
        else:     
            if "Access" not in current_vlan:
                channel.send(f'switchport mode Access \n')
                time.sleep(0.1)
                channel.send(f'no switchport trunk allowed vlan \n')
                time.sleep(0.1)
                channel.send(f'switchport access vlan {new_vlan} \n')
                time.sleep(0.2)
                channel.send(f'description VLAN_{new_vlan_text} \n')
                time.sleep(0.2)
                channel.send('end \n')
                time.sleep(0.2)
                channel.send(f'show running-config interface GigabitEthernet{switch_number}/0/{port_number} \n')
                time.sleep(0.1)
                output = collect_output(channel.recv(65535).decode('utf-8'))

            else :    

                #time.sleep(0.2)
                #channel.send('no desciption \n')
                time.sleep(0.2)
                channel.send(f'description VLAN_{new_vlan_text} \n')
                time.sleep(0.2)
                channel.send(f'no switchport access vlan {current_vlan} \n')
                time.sleep(0.2)
                channel.send(f'switchport access vlan {new_vlan} \n')
                time.sleep(0.2)
                channel.send('end \n')
                time.sleep(0.2)
                channel.send(f'show running-config interface GigabitEthernet{switch_number}/0/{port_number} \n')
                time.sleep(0.3)
                output = collect_output(channel.recv(65535).decode('utf-8'))

            # Collect and return output
            channel.close()
            client.close()
        return output
    except Exception as e:
        print(f"Error connecting to device: {e}")
        return None

#page des ports
@app.route('/ports', methods=['GET', 'POST'])

def show_ports():
    ports=get_ports()
    match = request.args.get('switch')  
    value = re.search(r'\d+', match)  # Recherche de chiffres dans la chaîne


    return render_template('port.html',ports=ports ,switch=value.group()) 

#api pour recuperer le statut du port locked/unlocked
@app.route('/api/port-locked-status/<switch>/<port>')
def port_locked_status(switch,port):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT locked FROM ports WHERE port = %s AND switch_n = %s', (port, switch))
    result = cursor.fetchone()
    locked = result[0] if result else 'unknown'  
    print(result)
    cursor.close()
    connection.close()
    return jsonify({'locked': locked})

#page admin
@app.route('/admin')
def admin():
    return render_template('admin.html')

#admin login
@app.route('/admin_login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        session['logged_in'] = True
        return redirect(url_for('admin_panel'))
    else:
        return 'Invalid credentials', 401
    
#admin panel
@app.route('/add_vlan', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    vlans = get_vlans()
    switches = get_switchs() 
    ports=get_ports()

    if request.method == 'POST':
        name=request.form.get('vlan_name')
        port=request.form.get('ports')
        type=request.form.get('type')

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO vlan(nom, port , type) VALUES (%s, %s,%s)", (name, port,type))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('admin_panel'))  # f5
    return render_template('admin_panel.html', vlans=vlans,switches=switches,ports=ports)

#màj de l'etat d'un port
@app.route('/toggle-lock/<string:switch>/<string:port>', methods=['POST'])
def toggle_lock(switch, port):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT locked FROM ports WHERE switch_n = %s AND port = %s", (switch, port))
    current_status = cursor.fetchone()
    new_status = 'no' if current_status[0] == 'yes' else 'yes'
    cursor.execute("UPDATE ports SET locked = %s WHERE switch_n = %s AND port = %s", (new_status, switch, port))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}

    
#suppression d'un vlan
@app.route('/delete_vlan', methods=['POST'])
def delete_vlan():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    vlan_id = request.form.get('vlan_id')
    if vlan_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vlan WHERE nom = %s', (vlan_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('VLAN supprimé avec succès.')
    else:
        flash('Erreur lors de la suppression du VLAN.')

    return redirect(url_for('admin_panel'))

#ajout d'un switch
@app.route('/add_switch', methods=['POST'])
def add_switch():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    name,num=parse_switch_name(request.form['switch_name'])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO switch (switch_name, switch_number) VALUES (%s, %s)', (name, num))
    insert_prt(num)
    conn.commit()
    cursor.close()
    conn.close()
    flash('Switch ajouté avec succès.')
    return redirect(url_for('admin_panel'))

#suppression de switch
@app.route('/delete_switch', methods=['POST'])
def delete_switch():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    switch_id = request.form['switch_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM switch WHERE switch_number = %s', (switch_id,))
    cursor.execute("DELETE FROM ports where switch_n=%s " ,(switch_id,))

    conn.commit()
    cursor.close()
    conn.close()
    flash('Switch supprimé avec succès.')
    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True)
