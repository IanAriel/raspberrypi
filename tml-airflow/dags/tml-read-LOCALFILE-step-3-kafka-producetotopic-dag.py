from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from datetime import datetime
from airflow.decorators import dag, task

######################################## USER CHOOSEN PARAMETERS ########################################
default_args = {
  'owner' : 'Sebastian Maurice',    
  'enabletls': 1,
  'microserviceid' : '',
  'producerid' : 'iotsolution',  
  'raw_data_topic' : 'iot-raw-data', # *************** This is one of the topic you created in SYSTEM STEP 2
  'identifier' : 'TML solution',  
  'inputfile' : '/rawdata/?',  # <<< ***** replace ?  to input file name to read. NOTE this data file should be JSON messages per line and stored in the HOST folder mapped to /rawdata folder 
  'delay' : 7000, # << ******* 7000 millisecond maximum delay for VIPER to wait for Kafka to return confirmation message is received and written to topic
  'topicid' : -999, # <<< ********* do not modify  
  'start_date': datetime (2024, 6, 29),
  'retries': 1,
    
}

######################################## USER CHOOSEN PARAMETERS ########################################

######################################## START DAG AND TASK #############################################

# Instantiate your DAG
@dag(dag_id="tml_localfile_step_3_kafka_producetotopic_dag", default_args=default_args, tags=["tml-localfile-step-3-kafka-producetotopic"], schedule=None,catchup=False)
def startproducingtotopic():
  # This sets the lat/longs for the IoT devices so it can be map
  VIPERTOKEN=""
  VIPERHOST=""
  VIPERPORT=""
    
  
  def producetokafka(value, tmlid, identifier,producerid,maintopic,substream,args):
     inputbuf=value     
     topicid=args['topicid']
  
     # Add a 7000 millisecond maximum delay for VIPER to wait for Kafka to return confirmation message is received and written to topic 
     delay = args['delay']
     enabletls = args['enabletls']
     identifier = args['identifier']

     try:
        result=maadstml.viperproducetotopic(VIPERTOKEN,VIPERHOST,VIPERPORT,maintopic,producerid,enabletls,delay,'','', '',0,inputbuf,substream,
                                            topicid,identifier)
     except Exception as e:
        print("ERROR:",e)

  @task(task_id="gettmlsystemsparams")         
  def gettmlsystemsparams():
    VIPERTOKEN = ti.xcom_pull(dag_id='tml_system_step_1_getparams_dag',task_ids='getparams',key="VIPERTOKEN")
    VIPERHOST = ti.xcom_pull(dag_id='tml_system_step_1_getparams_dag',task_ids='getparams',key="VIPERHOST")
    VIPERPORT = ti.xcom_pull(dag_id='tml_system_step_1_getparams_dag',task_ids='getparams',key="VIPERPORT")
    
    return [VIPERTOKEN,VIPERHOST,VIPERPORT]
        
  @task(task_id="readdata")        
  def readdata(params):
      args = default_args    
      basedir = '/'  
      inputfile=basedir + args['inputfile']

      # MAin Kafka topic to store the real-time data
      maintopic = args['raw_data_topic']
      producerid = args['producerid']
    
      k=0

      file1 = open(inputfile, 'r')
      print("Data Producing to Kafka Started:",datetime.datetime.now())

      while True:
        line = file1.readline()
        line = line.replace(";", " ")
        # add lat/long/identifier
        k = k + 1
        try:
          if not line or line == "":
            #break
            file1.seek(0)
            k=0
            print("Reached End of File - Restarting")
            print("Read End:",datetime.datetime.now())
            continue

          producetokafka(line.strip(), "", "",producerid,maintopic,"",args)
          # change time to speed up or slow down data   
          #time.sleep(0.15)
        except Exception as e:
          print(e)  
          pass  
  
      file1.close()
    
  readdata(gettmlsystemsparams())
    

dag = startproducingtotopic()
