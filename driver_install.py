import json # json reading/writing
import os #os directory and system calls
import logging # error logging
from subprocess import Popen # opening processes
import psutil# pid checking
import sys # sys exit
from time import sleep # sleep to check on status if proc is still running

# check if proc is running
def is_running ( pid ):
	if psutil.pid_exists( pid ):
		return True
	else:
		return False
# launch proc and return pid
def launch_n_detach ( proc_name ):
	try:
		process = Popen( proc_name )
		if ( is_running( process.pid ) ):
			log_m = ( "%r is running" % ( proc_name ) )
			logging_m ( log_m , "INFO" )
			return process.pid
	except:
		log_m = ( "Error %r failed to launch" % ( proc_name ) )#proc failed to launch
		logging_m ( log_m , "ERROR" )
		sys.exit()
# read json and output to data and output dict elements to a 1 layer driver_names dict
def json_read( driver_names ):
	with open ( "driver_status.json" ) as json_out :
		data = json.load ( json_out )

		print ( "Type : " , type( data ) )
		print ( data[ "Drivers" ] )
		for i in data[ "Drivers" ] :
			log_m = "Driver Name : " + i[ "Name" ] + " found in Json"
			logging_m( log_m , "INFO" ) 
			driver_names[ i[ "Name" ] ] = i[ "Status" ] 
			log_m =  "Status : " + i[ "Status" ]  + " found in Json"
			logging_m( log_m , "INFO" )
	return data, driver_names
# update json data variable
def json_write_new_drivers( data , driver_names ):
	cwd = os.getcwd()

	driver_dir = cwd + "/Drivers"
	for driver in os.listdir ( driver_dir ):
		log_m = driver + " found in Driver directory"
		logging_m( log_m , "INFO" )
		if ( driver not in driver_names ):
			log_m = driver + " added to json" 
			logging_m( log_m , "INFO" )
			data[ "Drivers" ].append( {
				"Name"		: driver,
				"Status"	: "Uninstalled"
				})
	return
# update status over driver in output json
def json_update_driver_status( data , d_name, status ):
	for i in data[ "Drivers" ] :
		if ( i[ "Name" ] == d_name ):
			i[ "Status" ] = status
			with open( "driver_status.json" , 'w' ) as json_in:
				json.dump( data , json_in , sort_keys = True , indent = 1 )
# logs for error checking 
def logging_m ( message , level ) :
	logging.basicConfig ( filename = "driver_status.log" , format = '%(asctime)s %(message)s ' , filemode = 'w' )
	logger = logging.getLogger()

	hash_lvl = {
	"DEBUG"		: logging.DEBUG,
	"INFO"		: logging.INFO,
	"WARNING"	: logging.WARNING,
	"ERROR"		: logging.ERROR,
	"CRITICAL"	: logging.CRITICAL,
	}

	logger.setLevel ( hash_lvl [ level ] )

	logger.info ( message )

	print ( message )

	return	
# runs the driver installation
def run( data , driver_names ):
	cwd = os.getcwd()
	driver_dir = cwd + "/Drivers"
	
	for driver in os.listdir ( driver_dir ):
		if ( driver_names[ driver ] == "Uninstalled" ):
			log_m = driver + " will now start installing, update json status to installing"
			json_update_driver_status( data , driver , "Installing" )
			logging_m( log_m , "INFO" )
			
			# early break so only first uninstalled driver is set to be installed since drivers require restart are installation
			driver_to_install = driver_dir + "/" + driver
			break

	log_m = "Changing directory to " + driver_dir
	logging_m( log_m , "INFO" )
	os.system( "cd " + driver_dir )

	# try to launch driver, if there is an uninstalled driver, if not all drivers are intstalled and script closes early
	try:
		pid = launch_n_detach( driver_to_install + " /s /i" )
		log_m = driver + " : PID is " + str( pid )
		logging_m( log_m , "INFO" )
	except:
		log_m = "All drivers installed, closing script"
		logging_m( log_m , "INFO" )
		sys.exit()

	while ( is_running( pid ) ):
		log_m = driver_to_install + " installation in progress"
		logging_m ( log_m , "INFO" )
		sleep( 60 )
	log_m = driver_to_install + " finished installing, restarting now"
	json_update_driver_status( data, driver, "Installed" )
	logging_m ( log_m , "INFO" )
	os.system( "shutdown /r /t 1" )

	return
def main() :
	driver_names = {}
	# check driver status in json
	data , driver_names =json_read( driver_names )

	# add new drivers to json and set to uninstalled
	json_write_new_drivers( data , driver_names )
	# write to json with new drivers set to uninstalled
	with open( "driver_status.json" , 'w' ) as json_in :
		json.dump ( data , json_in , sort_keys = True , indent = 1 )
	# run installation
	run ( data , driver_names )	

main()
