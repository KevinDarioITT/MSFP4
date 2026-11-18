# Práctica 4: Sistema Endóctrino

# Departamento de Ingeniería Eléctrica y Electrónica, Ingeniería Biomédica
# Tecnológico Nacional de México [TecNM - Tijuana]
# Blvd. Alberto Limón Padilla s/n, C.P. 22454, Tijuana, B.C., México

# Nombre del alumno: Kevin Dario De La Cruz Bojorquez
# Número de control: 20210777
# Correo institucional: kevin.delacruz201@tectijuana.edu.mx

# Asignatura: Modelado de Sistemas Fisiológicos
# Docente: Dr. Paul Antonio Valle Trujillo; Vsul.valle@tectijuana.edu.mx

# Instalar librerias en consola
# pip install numpy control matplotlib

# Liberias
import numpy as np
import control as ctrl
import matplotlib.pyplot as plt
 
# Datos Generales de la Simulacion
x0,t0,tend,dt,w,h = 0,0,10,1E-3,11,5
N = round(tend/dt) + 1
t = np.linspace(t0,tend,N)
Ve = np.ones(N)
 
#Componentes Circuito RLC
R1,L = 1E3, 100E-3
# Control
R2c,Cc = 100E3, 1E-6
# Caso
R2s,Cs = 1E3, 1000E-6
 
#Funcion de Transferencia
def rlc(R1,R2,L,C):
    num = [L,R2]
    den = [C*L*R1,C*R1*R2+L,R1+R2]
    return ctrl.tf(num,den)
 
sysControl = rlc(R1,R2c,L,Cc)
sysCaso = rlc(R1,R2s,L,Cs)
print(f"Función de transferencia Control: {sysControl}\n")
print(f"Función de transferencia Caso: {sysCaso}\n")
 
# Ganancias del controlador PID (de tu bloque PID de Simulink)
kP,kI,kD = 400,1200,0.5
 
# Componentes del controlador (circuito con Re, Ce, Rr, Cr)
# Vs/Ve = -(Re*Rr*Ce*Cr*s^2 + (Re*Ce + Rr*Cr)*s + 1) / (Re*Cr*s)
# Equivale a: kI = 1/(Re*Cr), kP = Rr/Re + Ce/Cr, kD = Rr*Ce
Cr = 1E-6                                   # se propone, puedes cambiarlo
if kP**2 < 4*kI*kD:
    raise ValueError("Con estas ganancias no hay solución real: kP^2 debe ser >= 4*kI*kD")
Re = 1/(Cr*kI)
RrCr = (kP + np.sqrt(kP**2 - 4*kI*kD))/(2*kI)   # producto Rr*Cr
Rr = RrCr/Cr
Ce = kD/Rr
print(f"Capacitancia Cr: {Cr:.3e} Faradios\n")
print(f"Resistencia Re: {Re:.3e} Ohms\n")
print(f"Resistencia Rr: {Rr:.3e} Ohms\n")
print(f"Capacitancia Ce: {Ce:.3e} Faradios\n")
 
# Controlador PID construido con los componentes
numPID = [Re*Rr*Ce*Cr,Re*Ce+Rr*Cr,1]
denPID = [Re*Cr,0]
PID = ctrl.tf(numPID,denPID)
print(f"Función de transferencia del controlador PID: {PID}\n")
 
# Sistema de control en lazo cerrado (PID aplicado al Caso)
sysPID = ctrl.feedback(ctrl.series(PID,sysCaso),1,sign = -1)
print(f"Funcion de transferencia en lazo cerrado: {sysPID}\n")
 
# Colores
clr1 = np.array([0,114,189])/255
clr2 = np.array([237,177,32])/255
clr3 = np.array([34,139,34])/255
clr4 = np.array([0.5,0.5,0.5])
 
# Funcion de respuesta
def response(t,sys,u):
    _,y = ctrl.forced_response(sys,t,u,x0)
    return y
 
# Respuestas: Simulaciones numéricas
VsControl = response(t,sysControl,Ve)
VsCaso = response(t,sysCaso,Ve)
VsPID = response(t,sysPID,Ve)
 
# Función: Respuestas de la simulación
def plotsignals(t,c,c1,c2,c3):
 
    fg = plt.figure(1)
    fg.set_size_inches(w,h)
    plt.rcParams['font.size'] = 11
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.plot(t,c,'-',color=clr1,linewidth=1.5,label=r'$Ve(t)$')
    plt.plot(t,c1,':',color=clr2,linewidth=1.5,label=r'$Vs(t)$: Control')
    plt.plot(t,c2,'--',color=clr3,linewidth=1.5,label=r'$Vs(t)$: Caso')
    plt.plot(t,c3,'--',color=clr4,linewidth=1.5,label=r'$Vs(t)$: Controlador PID')
    plt.xlim(-0.25,10); plt.xticks(np.arange(0,11,1))
    plt.ylim(0,1.1); plt.yticks(np.arange(0,1.2,0.1))
    plt.xlabel(r'$t$ [s]')
    plt.ylabel(r'$Vs(t)$ [V]')
    plt.legend(title='Control y caso',bbox_to_anchor=(0.5,1.0),loc='lower center',ncol=4,frameon=False)
    plt.show()
    fg.savefig('Control_caso_python.pdf',bbox_inches='tight')
 
# Respuesta al escalón: Control y caso
plotsignals(t,Ve,VsControl,VsCaso,VsPID)
 