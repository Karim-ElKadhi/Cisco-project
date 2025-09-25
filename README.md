# Cisco Project  

This project provides a **web-based interface** to manage VLAN configurations on Cisco switches.  
It simplifies the process of connecting **Home Gateways to the WAN network** by allowing administrators to assign VLANs to specific switch ports.  

## 🚀 Features  
- **VLAN Management**  
  - Configure **Access Ports**: assign a single VLAN to a port for end devices (e.g., Home Gateways).  
  - Configure **Trunk Ports**: allow multiple VLANs on a single port for uplinks between switches or routers.  

- **Admin Section**  
  - Add and manage switches.  
  - Add and configure ports (access or trunk).  
  - Lock/Unlock ports for security control.  
  - Manage multiple connected devices with ease.  

## 🛠️ Project Structure  
Cisco-project/
│── app/ # Application core logic
│── static/ # Static assets (CSS, JS, images)
│── templates/ # HTML templates for the web interface
│── AppCisco.py # Main application script
│── wsgi.py # Entry point for deployment (WSGI server)

markdown
Copier le code

## ⚙️ Requirements  
- Python 3.x  
- Flask (for the web interface)  
- Netmiko / Paramiko (for Cisco switch communication)  

Install dependencies:  
```bash
pip install -r requirements.txt
```
▶️ Usage
Clone the repository:

```bash
git clone https://github.com/yourusername/Cisco-project.git
cd Cisco-project
```
Run the application:

```bash
python AppCisco.py
```
Access the interface in your browser:
http://localhost:5000

## 🔐 Admin Features
Add new switches to manage.

Define and configure Access and Trunk ports.

Assign VLANs to access ports.

Define allowed VLANs on trunk ports.

Lock/Unlock ports to prevent unauthorized access.

## 📸 Screenshots
Interface examples from the project:

![Switch Selection](./Screenshot%202025-09-25%20at%2016-00-39%20Sélection%20du%20Switch.png)  
![Port Management](./Screenshot%202025-09-25%20at%2015-55-32%20Port%20Layout.png)  
![Vlan Selection](./Screenshot%20from%202025-09-25%2016-06-14.png) 


## 📜 License
This project is licensed under the MIT License.
