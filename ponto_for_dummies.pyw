# criado por Lucas Costa <lucas.script@gmail.com> 02-12-2015
import time
import datetime
import re
from urllib.request import urlopen
import json
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import winsound

# data a ser ignorada
ignore_date = None
# intervalo de data a ser ignorado
ignore_time = None

def verify_regs():
	current_date = datetime.datetime.now()
	
	# verificando se o alerta deve ser ignorado
	if ignore_date == current_date.date():
		return
	if ignore_time != None:
		if current_date <= ignore_time:
			return
	
	# rotina de verificacao
	config_json = json.load(open('.\\config\\config.json'))
	# cpf
	cpf = process_cpf(config_json['cpf'])
	# message
	message = str(config_json['message'])
	# message color
	message_color = str(config_json['message_color'])
	# api url
	api_url = str(config_json['api'])
	# api grade url
	api_grade_url = str(api_url + '/grade/' + cpf)
	
	# conecta a api para buscar a grade do usuario
	grade_json = urlopen(api_grade_url).read()
	# carrega json retornado pela api
	grade_json_read = json.loads(grade_json.decode('utf-8'))
	# monta o objeto grade
	grade = {1: int(grade_json_read['entrada_1'].replace(':', '')), 
				2: int(grade_json_read['saida_1'].replace(':', '')), 
				3: int(grade_json_read['entrada_2'].replace(':', '')), 
				4: int(grade_json_read['saida_2'].replace(':', ''))}
	# monta o objeto de registros
	regs = {1: False, 2: False, 3: False, 4: False}
	# monta url para consulta dos registros de hoje
	api_registros_url = str(api_url + '/hoje/' + cpf)
	# conecta a api para buscar os registros do usuario
	registros_json = urlopen(api_registros_url).read()
	# carrega json retornado pela api
	registros_json_read = json.loads(registros_json.decode('utf-8'))
	# objeto situação da grade atual
	situacao_atual_ponto = ""
	
	# para cada registro retornado
	for row in registros_json_read:
		# index do registro
		index = int(row['etapa'])
		# registro encontrado
		regs[index] = True
		# monta a string da situação atual
		situacao_atual_ponto = situacao_atual_ponto + str(row['hora']) + ":" + str(row['minutos']) + "   "
		
	# para cada registro
	for reg in regs:
		# verifica se o registro aconteceu
		if regs[reg] == False:
			# hora atual
			current_hour = current_date.hour
			# minuto atual
			current_minutes = str(current_date.minute)
			# tratamento do minuto adiciona 0 quando o: 0 < minuto < 9 
			if len(current_minutes) == 1:
				current_minutes = "0" + current_minutes
				
			# monta a hora para comparação, exe: 16:30 -> 1630 , 08:00 -> 800
			current_time = int(str(current_date.hour) + current_minutes)
			# verifica caso a hora atual esteja entre as grades mostra o aviso
			if grade[reg] <= current_time <= next_reg_limit(reg, grade):
				show_warning("Seus Registros\n" + situacao_atual_ponto + "\n\n\n" + message, message_color)

# busca o horario limite para o próximo registro	 	
def next_reg_limit(reg, grade):
	if reg >= 4:
		# horario limite para 4º registro 22:00 -> 2200
		return 2200
	else:
		# caso contrário pega próximo registro da grade
		return grade[reg+1]

# mostra a mensagem
def show_warning(message, message_color):
	# monta a janela principal
	root = tk.Tk()
	root.resizable(width=False, height=False)
	# importa a imagem que será usada como background
	bg_img = Image.open('.\\config\\bg-img.jpg')
	tk_img = ImageTk.PhotoImage(bg_img)
	# seta o título da janela
	root.title("ponto_for_dummies")
	# pega as dimensões do monitor usado
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()
	x = int((screen_width/2) - 250)
	y = int((screen_height/2) - 250)
	# seta a geometria para centralizar a janela
	geometry = "500x500+" + str(x) + "+" + str(y)
	root.geometry(geometry)
	# cria os botões
	tk.Button(root, text="Não receber notificações hoje", fg="black", command=add_ignore_date).pack()
	tk.Button(root, text="Adiar notificações por 15min", fg="black", command=add_ignore_15).pack()
	tk.Button(root, text="Adiar notificações por 30min", fg="black", command=add_ignore_30).pack()
	tk.Button(root, text="Adiar notificações por 1h", fg="black", command=add_ignore_60).pack()
	# monta o texto dentro da janela
	tk.Label(root, image=tk_img, text=message, compound=tk.CENTER, font=('times', 20, 'bold'), fg=message_color).pack()
	# coloca a janela na frente das outras janelas abertas
	root.wm_attributes("-topmost", 1)
	# força o focu na janela
	root.focus_force()
	# executa o som do alerta
	winsound.PlaySound('.\\config\\alert.wav', winsound.SND_FILENAME)
	# mantem a janela ativa
	root.mainloop()

# adiciona data a ser ignorada
def add_ignore_date():
	global ignore_date
	ignore_date = datetime.datetime.now().date()
	messagebox.showinfo("info", "Ok, sem mais notificações por hoje")
	return

# adiciona intervalo a ser ignorado
def add_ignore_15():
	return add_ignore_time(15)
	
def add_ignore_30():
	return add_ignore_time(30)
	
def add_ignore_60():
	return add_ignore_time(60)
	
def add_ignore_time(minutes):
	global ignore_time
	global ignore_time_delta
	ignore_time = datetime.datetime.now() + datetime.timedelta(minutes=int(minutes))
	messagebox.showinfo("info", "Você não receberá mais notificações por " + str(minutes) + " min")
	return

# remove caracteress especiais e zeros à esquerda do cpf
def process_cpf(cpf):
	return re.sub('[^A-Za-z0-9]+', '', cpf).lstrip("0")

# escreve no log de erro
def write_error_log(error):
	log = open('.\\config\\error.log', 'w')
	log.truncate()
	log.write('Erro: ' + str(error) + '\n')
	log.close()
	
def tick():
	print('tick! %s' % datetime.datetime.now().time())
	try:
		verify_regs()
	except Exception as e:
		print('Error :' + str(e))
		write_error_log(str(e))
	return

if __name__ == '__main__':
	print("ponto for dummies - iniciado...")
	while True:
		tick()
		time.sleep(60)