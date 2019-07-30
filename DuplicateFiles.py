import os
import hashlib
import time
import psutil
import urllib.request
import smtplib
import schedule
from sys import *
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

#Deletes the Duplicate Files
def DeleteDuplicate(dict,dupfile):
	result = list(filter(lambda x: len(x) > 1, dict.values()))
	icnt = 0
	dupfile.write("Duplicate Files:\n")
	if len(result)>0:
		print("Duplicate Found")

		print("The Following are same ")	
		for res in result:
			for subres in res:
				icnt+=1
				if icnt>=2:
					dupfile.write(f"\t[deleted] {subres}\n")
					os.remove(subres)
					icnt=0
				else:
					print("No duplicates file found")		

#To check whether connection is established or not
def is_connected():
	try:
		urllib.request.urlopen('http://216.58.192.142',timeout=1)
		return True
	except urllib.request.URLError as err:
		return False

def MailSender(filename,time):
	try:
		fromaddr = "abc@gmail.com"
		toaddr = "xyz@gmail.com"

		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddr
		body = """
		Hello %s, 
		Please find attached document which contains Log of Deleted Files
		Log file is created at: %s

		This is auto generated mail.

		Thanks & Regards,
		Your_Name
		"""%(toaddr,time)


		Subject = """Log Generated at: %s"""%(time)

		msg['Subject']=Subject
		msg.attach(MIMEText(body,'plain'))
		attachment = open(filename,"rb")
		p = MIMEBase('application','octet-stream')
		p.set_payload((attachment).read())
		encoders.encode_base64(p)
		p.add_header('Content-Disposition',"attachment;filename=%s"%filename)
		msg.attach(p)
		s = smtplib.SMTP('smtp.gmail.com',587)
		s.starttls()
		s.login(fromaddr,"***********")
		text = msg.as_string()
		s.sendmail(fromaddr,toaddr,text)
		s.quit()

		print("Log file successfully sent through mail")
	except Exception as E:
		print("Unable to send mail ",E)

#checksum of file
def hashfile(path,blocksize = 1024):
	afile = open(path,'rb')
	hasher = hashlib.md5()
	buf = afile.read(blocksize)

	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
		afile.close()

		return hasher.hexdigest()

def FindDuplicate(path):
	flag = os.path.isabs(path)
	if(flag==False):
		path = os.path.abspath(path)

		exist = os.path.isdir(path)
		dups={}

		if(exist):
			for foldername,subfolder,fileList in os.walk(path):
				print("Current Folder is :"+foldername)
				for filen in fileList:
					path = os.path.join(foldername,filen)
					file_hash = hashfile(path)
					if file_hash in dups:
						dups[file_hash].append(path)
					else:
						dups[file_hash] = [path]
			return dups

		else:
			print("Invalid Path")

#For printing the Duplicate Files
def printDuplicate(dict):
	result = list(filter(lambda x: len(x)>1, dict.values()))
	if(len(result)>0):
		print("The Following are duplicate files")
		for res in result:
			for subres in res:
				print('\t\t%s'%subres)
	else:
		print("No Duplicate files found")

def Proceed(dirname):
	try:
		connected = is_connected()
		if connected:
			seperator="-" * 80
			log_path = os.path.join(dirname,'LogFile.log')
			f = open(log_path,'w')
			print("Done2")
			f.write(seperator+"\n")
			f.write("Duplicate Logger: "+time.ctime()+"\n")
			f.write(seperator+"\n")
			f.write("\n")
			arr={}
			startTime = time.time()
			arr = FindDuplicate(dirname)
			printDuplicate(arr)
			DeleteDuplicate(arr,f)
			endTime = time.time()
			MailSender(f,time.ctime())
			f.close()
			print("Took %s seconds to evaluate"%(endTime-startTime))
		else:
			print("Connection not established")
			exit()
	except Exception as E:
				print("Error: Invalid input",E)	

def Main():
	print("---Deletion of Duplicate Files---")
	print("Application name : "+argv[0])
	print(argv[1])
	#print(argv[2])

	if(len(argv)>3):
		print("Error: Invalid Number of Arguments")
		exit()

	#help
	if(argv[1]=="-h") or (argv[1]=="-H"):
		print("This Script is used to traverse specific directory and delete duplicates of files")
		exit()

	#usage
	if(argv[1]=="-u") or (argv[1]=="-U"):
		print("Usage: Filename Time_Interval Directory_name")
		print("Filename: Script File")
		print("")
		print("Directory_name: Directory of Duplicate Files")
		exit()

	try:
		schedule.every(int(argv[1])).minutes.do(Proceed,argv[2])
		while True:
			schedule.run_pending()
			time.sleep(1)
	except ValueError:
		print("Error: Invalid datatype of input")
	except Exception as E:
		print("Error: Invalid input",E)
	except ValueError:
		print("Error : Invalid Datatype of Input")

if __name__=="__main__":
	Main()