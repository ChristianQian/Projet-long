import processing.serial.*;
Serial myPort; 
Table dataTable;

int readingCounter = 0;
int numReadings = 10;
String fileName;

void setup() {
   String portName = Serial.list()[0]; 
   myPort = new Serial(this, portName, 9600);//portName, 9600); //set up your port to listen to the serial port
   myPort.bufferUntil('\n');
   
   dataTable = new Table();
   dataTable.addColumn("Jour");
   dataTable.addColumn("Mois");
   dataTable.addColumn("Heure");
   dataTable.addColumn("Minutes");
   dataTable.addColumn("Secondes");
   dataTable.addColumn("Lieu");
   dataTable.addColumn("Couloir");
   dataTable.addColumn("Temperature");
   dataTable.addColumn("Humidite");
   dataTable.addColumn("Particules");
   dataTable.addColumn("Qualite");
   dataTable.addColumn("Son");
}

void draw() {}

void serialEvent(Serial myPort) {
  try {
    String val = myPort.readStringUntil('\n'); //The newline separator separates each Arduino loop. We will parse the data by each newline separator. 
    if (val!= null) { //We have a reading! Record it.
      val = trim(val); //gets rid of any whitespace or Unicode nonbreakable space
      println(val); //Optional, useful for debugging. If you see this, you know data is being sent. Delete if  you like. 
      float sensorVals[] = float(split(val, ';')); //parses the packet from Arduino and places the valeus into the sensorVals array. I am assuming floats. Change the data type to match the datatype coming from Arduino. 
      int salle = 3051;
      int couloir = 1;
      TableRow newRow = dataTable.addRow();
      newRow.setInt("Jour", day());
      newRow.setInt("Mois", month());
      newRow.setInt("Heure", hour());
      newRow.setInt("Minutes", minute());
      newRow.setInt("Secondes", second());
      
      newRow.setInt("Lieu", salle);
      newRow.setInt("Couloir", couloir);
      
      newRow.setFloat("Temperature", sensorVals[0]);
      //print("RObert "+ sensorVals[0]);
      newRow.setFloat("Humidite", sensorVals[1]);
      //newRow.setFloat("Particules", sensorVals[2]);
      newRow.setFloat("Qualite", sensorVals[2]);
      newRow.setFloat("Son", sensorVals[3]);
      
      readingCounter++;
      
      if (readingCounter == numReadings)//The % is a modulus, a math operator that signifies remainder after division. The if statement checks if readingCounter is a multiple of numReadings (the remainder of readingCounter/numReadings is 0)
      {
        //fileName = str(year()) + str(month()) + str(day()) + str(dataTable.lastRowIndex()); //this filename is of the form year+month+day+readingCounter
        fileName = "../data/"+str(year()) + str(month()) + str(day()) + str(salle) + str(couloir)+".csv";
        saveTable(dataTable, fileName); //Woo! save it to your computer. It is ready for all your spreadsheet dreams. 
      }
    }
  } catch(RuntimeException e) { e.printStackTrace(); }
}
