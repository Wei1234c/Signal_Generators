#pragma NOIV					// Do not generate interrupt vectors
//-----------------------------------------------------------------------------
//	File:		AD5570.c
//	Contents:	Hooks required to implement USB peripheral function.
//
//	Copyright (c) 2000 Cypress Semiconductor All rights reserved
//-----------------------------------------------------------------------------
#include "fx2.h"
#include "Fx2regs.h"
#include <math.h>

extern BOOL	GotSUD;			// Received setup data flag
extern BOOL	Sleep;
extern BOOL	Rwuen;
extern BOOL	Selfpwr;

BYTE	Configuration;		// Current configuration
BYTE	AlternateSetting;	// Alternate settings

//-----------------------------------------------------------------------------
// Constants
//-----------------------------------------------------------------------------
#define	VR_UPLOAD		0xc0
#define VR_DOWNLOAD		0x40

#define VR_ANCHOR_DLD   0xa0 // handled by core
#define VR_EEPROM		0xa2 // loads (uploads) EEPROM
#define	VR_RAM			0xa3 // loads (uploads) external ram
#define VR_SETI2CADDR	0xa4
#define VR_GETI2C_TYPE  0xa5 // 8 or 16 byte address
#define VR_GET_CHIP_REV 0xa6 // Rev A, B = 0, Rev C = 2 // NOTE: New TNG Rev
#define VR_TEST_MEM     0xa7 // runs mem test and returns result
#define VR_RENUM	    0xa8 // renum
#define VR_DB_FX	    0xa9 // Force use of double byte address EEPROM (for FX)
#define VR_I2C_100    0xaa // put the i2c bus in 100Khz mode
#define VR_I2C_400    0xab // put the i2c bus in 400Khz mode
#define VR_NOSDPAUTO  0xac // test code. does uploads using SUDPTR with manual length override

//#define	VR_ReadContData	0xdc

//-----Transfer Types Constants-----------------------

#define VR_SPI			0xdd		//Standard SPI transfer (max 32 bits)
#define VR_ADF4193TRIG	0xd9		//Transfer Register contents and Send TRIG and LE High simultaneously (trigger signal for Locktime)
#define VR_ADC			0xda		//unused
#define VR_PINS			0xde		//unused
#define VR_DIR_D1		0xdc		//unused
#define VR_DIR_D0		0xdb		//unused
#define VR_CLK			0xdf		// new command
#define VR_CE_PDRF      0xd8        //CE and PDRF settings
//------------------------------------------------------
	
//#define VR_INTSTATUS		0xdf

#define SERIAL_ADDR		0x50
#define EP0BUFF_SIZE	0x40

//SPI interface definitions

#define SETDIN		IOA |= 0x04
#define CLRDIN		IOA &= 0xfb
#define SETCLK		IOA |= 0x02			// Pin assignments for TSM Proto Board
#define CLRCLK		IOA &= 0xfd		
#define SETLE		IOA |= 0x01
#define CLRLE		IOA &= 0xfe
#define SETTRIG		IOA |= 0x09
#define CLRTRIG		IOA &= 0xf6

#define SETCE		IOA |= 0x40
#define CLRCE		IOA &= 0xBF

#define SETPDRF		IOA |= 0x20
#define CLRPDRF		IOA &= 0xDF




//#define SETDIN		IOA |= 0x20
//#define CLRDIN		IOA &= 0xdf
//#define SETCLK		IOA |= 0x40
//#define CLRCLK		IOA &= 0xbf				// Pin Assignments for DAC Boards
//#define SETCS		IOA |= 0x80
//#define CLRCS		IOA &= 0x7f

#define SETLDAC		IOA |= 0x10
#define CLRLDAC		IOA &= 0xef
#define SETCLR		IOA |= 0x08
#define CLRCLR		IOA &= 0xf7

//#define SETMUXDIN	IOB |= 0x01
//#define CLRMUXDIN	IOB &= 0xfe

#define GET_CHIP_REV()		((CPUCS >> 4) & 0x00FF) // EzUSB Chip Rev Field

//-----------------------------------------------------------------------------
// Global Variables
//-----------------------------------------------------------------------------
BYTE			DB_Addr;					//TPM Dual Byte Address stat
BYTE			I2C_Addr;					//TPM I2C address
BOOL			ContDataReady;
BYTE			TempStorage[30];

//-----------------------------------------------------------------------------
// Prototypes
//-----------------------------------------------------------------------------
void EEPROMWrite(WORD addr, BYTE length, BYTE xdata *buf); //TPM EEPROM Write
void EEPROMRead(WORD addr, BYTE length, BYTE xdata *buf);  //TPM EEPROM Read

BYTE Read_SPI(unsigned long word, BYTE NumBytes, BYTE ptrB);
void Write_SPI(int Bits,unsigned long Word);
void Write_SPI_TRIG(int Bits,unsigned long Word);
void Read_VCO_Data(void);
void set_ce_pdrf(int ce_pdrf_data);

//-----------------------------------------------------------------------------
// Task Dispatcher hooks
// The following hooks are called by the task dispatcher.
//-----------------------------------------------------------------------------

void TD_Init(void) 				// Called once at startup
{
Rwuen = TRUE;					// Enable remote-wakeup
CPUCS = (CPUCS & 0xe7) | 0x10;	// 48MHz
OEA = 0xff;						//direction bits on portA, All outputs
IOA = 0x9f; 					//SYNC 1, SCLK 0, SDIN 0, LDAC 1, CLR 1, Bin2sC 1, RSTIN 1, CSADC 1
OEB = 0x00;						//direction bits on portB, All inputs 

//ContDataReady = FALSE;
}

void TD_Poll(void) 				// Called repeatedly while the device is idle
{

}

BOOL TD_Suspend(void) 			// Called before the device goes into suspend mode
{
	return(TRUE);
}

BOOL TD_Resume(void) 			// Called after the device resumes
{
	return(TRUE);
}

//-----------------------------------------------------------------------------
// Device Request hooks
//	The following hooks are called by the end point 0 device request parser.
//-----------------------------------------------------------------------------


BOOL DR_GetDescriptor(void)
{
   return(TRUE);
}

BOOL DR_SetConfiguration(void)   // Called when a Set Configuration command is received
{
   Configuration = SETUPDAT[2];
   return(TRUE);            // Handled by user code
}

BOOL DR_GetConfiguration(void)   // Called when a Get Configuration command is received
{
   EP0BUF[0] = Configuration;
   EP0BCH = 0;
   EP0BCL = 1;
   return(TRUE);            // Handled by user code
}

BOOL DR_SetInterface(void)       // Called when a Set Interface command is received
{
   AlternateSetting = SETUPDAT[2];
   return(TRUE);            // Handled by user code
}

BOOL DR_GetInterface(void)       // Called when a Set Interface command is received
{
   EP0BUF[0] = AlternateSetting;
   EP0BCH = 0;
   EP0BCL = 1;
   return(TRUE);            // Handled by user code
}

BOOL DR_GetStatus(void)
{
   return(TRUE);
}

BOOL DR_ClearFeature(void)
{
   return(TRUE);
}

BOOL DR_SetFeature(void)
{
   return(TRUE);
}

BOOL DR_VendorCmnd(void)
{
BYTE Data, Control,	ptrB;
int Bits, ce_pdrf_data;
unsigned long Word;

	switch(SETUPDAT[1])
		{ 
		case VR_SPI:								//SPI Interface
	
			if (SETUPDAT[0] == VR_DOWNLOAD)
				{
				EP0BCH = 0;
				EP0BCL = 0;
				while(EP0CS & bmEPBUSY);					
				Word = EP0BUF[0] + EP0BUF[1]*256 + EP0BUF[2]*65536 + EP0BUF[3]*16777216;
				Bits = EP0BUF[4];
				Write_SPI(Bits,Word);
				}
			
			if (SETUPDAT[0] == VR_UPLOAD)
				{	
				while(EP0CS & bmEPBUSY);
				Data = 0;
				Control = SETUPDAT[2];
				Word = Control * 65536 + Data;
				ptrB = Read_SPI(Word,1,0);
				EP0BCH = 0;
				EP0BCL = 2;  // Arm endpoint with # bytes to transfer
			    }
		break;


		case VR_ADF4193TRIG:

			if (SETUPDAT[0] == VR_DOWNLOAD)
			{
			EP0BCH = 0;
			EP0BCL = 0;
			while(EP0CS & bmEPBUSY);
			Word = EP0BUF[0] + EP0BUF[1]*256 + EP0BUF[2]*65536 + EP0BUF[3]*16777216;
			Bits = EP0BUF[4];
			Write_SPI_TRIG(Bits,Word);
			}
		 break;

 		case VR_CLK:

//			EP0BCH = 0;
//			EP0BCL = 0;
			while(EP0CS & bmEPBUSY);		// ensures the USB is available for transfers
			//	Data = 0;
			//	Control = SETUPDAT[2];
			//	Word = Control * 65536 + Data;
			//	ptrB = Read_SPI(Word,1,0);
				Read_VCO_Data();

				EP0BCH = 0;
				EP0BCL = 2;  // Arm endpoint with # bytes to transfer
		 break;

		 case VR_CE_PDRF:

		 EP0BCH = 0;
		 EP0BCL = 0;
		 while(EP0CS & bmEPBUSY);
		 ce_pdrf_data = EP0BUF[0];
         set_ce_pdrf(ce_pdrf_data);

		 break;
			
		}
return(FALSE);
}


void Read_VCO_Data(void)
{
	
	BYTE k,i,j;
	BYTE ReturnData[2];
	unsigned long BitTest;	

	SETLE;
	SETDIN;
  						
//	CLRCLK;
//	CLRLE;

	ReturnData[0] = 0;
	ReturnData[1] = 0;


	for(k=0;k<2;k++)						// D9, D8
		{
				

			SETCLK;			
			
			for(i=0;i<4;i++)				//Delay
			{}			
			
			// read
			ReturnData[0] = ReturnData[0] << 1;
			BitTest = IOB & 0x01;			// 0000 000x where x = data bit 
			ReturnData[0] = ReturnData[0] | BitTest; 

			CLRCLK;
			for(i=0;i<4;i++)				//Delay
			{}			
		}

	for(k=0;k<8;k++)						// D7 - D0
		{
			
		    
			SETCLK;			
			
			for(i=0;i<4;i++)				//Delay
			{}			
			
			// read
			ReturnData[1] = ReturnData[1] << 1;
			BitTest = IOB & 0x01;			// 0000 000x where x = data bit 
			ReturnData[1] = ReturnData[1] | BitTest; 	
		
			CLRCLK;
			for(i=0;i<4;i++)				//Delay
			{}			
		}



	  EP0BUF[0] = ReturnData[0];
	  EP0BUF[1] = ReturnData[1];
//	*(EP0BUF) |= ReturnData[0] << 8;	//set return value here
		
	CLRCLK;	
//	SETLE;	

}


void set_ce_pdrf(int ce_pdrf_data)
{
      CLRCE;
	  CLRPDRF;
	
 	if(ce_pdrf_data == 0x4)
    {
		CLRCE;
		CLRPDRF;
	}

	if(ce_pdrf_data == 0x14)
    {
		CLRCE;
		SETPDRF;
	}

	if(ce_pdrf_data == 0xC)
    {
		SETCE;
		CLRPDRF;
	}

    if(ce_pdrf_data == 0x1C)
    {
		SETCE;
		SETPDRF;
	}
	
}



BYTE Read_SPI(unsigned long Word, BYTE NumBytes, BYTE ptrB)
{
BYTE j,k,i;
WORD  ReturnData[2];
unsigned long BitTest;

	SETLE;						
	CLRCLK;
	CLRLE;	
	CLRDIN;
	for(j=0;j<NumBytes;j++)
		{
		ReturnData[j] = 0;	
		for(k=0;k<24;k++)
			{
			if(BitTest == (Word & BitTest))
				SETDIN;
			else
				CLRDIN;
			BitTest = BitTest >> 1;

			SETCLK;			
			ReturnData[j] = (ReturnData[j] << 1) | (IOB & 0x80);			
			CLRCLK;
			for(i=0;i<4;i++)				//Delay
			{}	
			}
		*(EP0BUF + ptrB++) = ReturnData[j];
		*(EP0BUF + ptrB++) = ReturnData[j] >> 8;	//set return value here
		*(EP0BUF + ptrB++) = ReturnData[j] >> 8;

		}	
	CLRCLK;	
	SETLE;	
	return(ptrB);
}

void Write_SPI(int Bits,unsigned long Word)
{
unsigned long BitTest;
BYTE i,j;
	
	BitTest = (pow (2,Bits)) / 2;
	CLRLE;
	for(j=0;j<Bits;j++)
		{
			if( BitTest == (Word & BitTest) )
				SETDIN;
			else 
				CLRDIN;
				BitTest = BitTest >> 1;		//Shift BitTest to the right by one bit
			SETCLK;
			for(i=0;i<4;i++)			//Delay
			{}
			CLRCLK;
		}			
	for(i=0;i<4;i++)				//Delay
	{}					
	SETLE;
	for(i=0;i<4;i++)				//Delay
	{}
	CLRLE;

}


void Write_SPI_TRIG(int Bits,unsigned long Word)
{
unsigned long BitTest;
BYTE i,j;
	
	BitTest = (pow (2,Bits)) / 2;
	CLRTRIG;
	for(j=0;j<Bits;j++)
		{
			if( BitTest == (Word & BitTest) )
				SETDIN;
			else 
				CLRDIN;
				BitTest = BitTest >> 1;		//Shift BitTest to the right by one bit
			SETCLK;
			for(i=0;i<4;i++)			//Delay
			{}
			CLRCLK;
		}			
	for(i=0;i<4;i++)				//Delay
	{}					
	SETTRIG;
	for(i=0;i<4;i++)				//Delay
	{}
	CLRTRIG;
}



	


//-----------------------------------------------------------------------------
// USB Interrupt Handlers
//	The following functions are called by the USB interrupt jump table.
//-----------------------------------------------------------------------------

// Setup Data Available Interrupt Handler

void ISR_Sudav(void) interrupt 0
{
   // enable the automatic length feature of the Setup Data Autopointer
   // in case a previous transfer disbaled it
   SUDPTRCTL |= bmSDPAUTO;

   GotSUD = TRUE;            // Set flag
   EZUSB_IRQ_CLEAR();
   USBIRQ = bmSUDAV;         // Clear SUDAV IRQ
}

// Setup Token Interrupt Handler
void ISR_Sutok(void) interrupt 0
{
   EZUSB_IRQ_CLEAR();
   USBIRQ = bmSUTOK;         // Clear SUTOK IRQ
}

void ISR_Sof(void) interrupt 0
{
   EZUSB_IRQ_CLEAR();
   USBIRQ = bmSOF;            // Clear SOF IRQ
}

void ISR_Ures(void) interrupt 0
{
   if (EZUSB_HIGHSPEED())
   {
      pConfigDscr = pHighSpeedConfigDscr;
      pOtherConfigDscr = pFullSpeedConfigDscr;
   }
   else
   {
      pConfigDscr = pFullSpeedConfigDscr;
      pOtherConfigDscr = pHighSpeedConfigDscr;
   }
   
   EZUSB_IRQ_CLEAR();
   USBIRQ = bmURES;         // Clear URES IRQ
}

void ISR_Susp(void) interrupt 0
{
   Sleep = TRUE;
   EZUSB_IRQ_CLEAR();
   USBIRQ = bmSUSP;
}

void ISR_Highspeed(void) interrupt 0
{
   if (EZUSB_HIGHSPEED())
   {
      pConfigDscr = pHighSpeedConfigDscr;
      pOtherConfigDscr = pFullSpeedConfigDscr;
   }
   else
   {
      pConfigDscr = pFullSpeedConfigDscr;
      pOtherConfigDscr = pHighSpeedConfigDscr;
   }

   EZUSB_IRQ_CLEAR();
   USBIRQ = bmHSGRANT;
}

void ISR_Ep0ack(void) interrupt 0
{
}
void ISR_Stub(void) interrupt 0
{
}
void ISR_Ep0in(void) interrupt 0
{
}
void ISR_Ep0out(void) interrupt 0
{
}
void ISR_Ep1in(void) interrupt 0
{
}
void ISR_Ep1out(void) interrupt 0
{
}
void ISR_Ep2inout(void) interrupt 0
{
}
void ISR_Ep4inout(void) interrupt 0
{
}
void ISR_Ep6inout(void) interrupt 0
{
}
void ISR_Ep8inout(void) interrupt 0
{
}
void ISR_Ibn(void) interrupt 0
{
}
void ISR_Ep0pingnak(void) interrupt 0
{
}
void ISR_Ep1pingnak(void) interrupt 0
{
}
void ISR_Ep2pingnak(void) interrupt 0
{
}
void ISR_Ep4pingnak(void) interrupt 0
{
}
void ISR_Ep6pingnak(void) interrupt 0
{
}
void ISR_Ep8pingnak(void) interrupt 0
{
}
void ISR_Errorlimit(void) interrupt 0
{
}
void ISR_Ep2piderror(void) interrupt 0
{
}
void ISR_Ep4piderror(void) interrupt 0
{
}
void ISR_Ep6piderror(void) interrupt 0
{
}
void ISR_Ep8piderror(void) interrupt 0
{
}
void ISR_Ep2pflag(void) interrupt 0
{
}
void ISR_Ep4pflag(void) interrupt 0
{
}
void ISR_Ep6pflag(void) interrupt 0
{
}
void ISR_Ep8pflag(void) interrupt 0
{
}
void ISR_Ep2eflag(void) interrupt 0
{
}
void ISR_Ep4eflag(void) interrupt 0
{
}
void ISR_Ep6eflag(void) interrupt 0
{
}
void ISR_Ep8eflag(void) interrupt 0
{
}
void ISR_Ep2fflag(void) interrupt 0
{
}
void ISR_Ep4fflag(void) interrupt 0
{
}
void ISR_Ep6fflag(void) interrupt 0
{
}
void ISR_Ep8fflag(void) interrupt 0
{
}
void ISR_GpifComplete(void) interrupt 0
{
}
void ISR_GpifWaveform(void) interrupt 0
{
}


