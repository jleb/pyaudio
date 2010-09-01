/** @file patest_read_record.c
	@brief Record input into an array; Save array to a file; Playback recorded
    data. Implemented using the blocking API (Pa_ReadStream(), Pa_WriteStream() )
	@author Phil Burk  http://www.softsynth.com
    @author Ross Bencina rossb@audiomulch.com
*/
/*
 * $Id: patest_read_record.c 757 2004-02-13 07:48:10Z rossbencina $
 *
 * This program uses the PortAudio Portable Audio Library.
 * For more information see: http://www.portaudio.com
 * Copyright (c) 1999-2000 Ross Bencina and Phil Burk
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files
 * (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge,
 * publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * Any person wishing to distribute modifications to the Software is
 * requested to send the modifications to the original developer so that
 * they can be incorporated into the canonical version.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
 * ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include "portaudio.h"

/* #define SAMPLE_RATE  (17932) /* Test failure to open with this value. */
#define SAMPLE_RATE  (44100)
#define FRAMES_PER_BUFFER (1024)
#define NUM_SECONDS     (5)
#define NUM_CHANNELS    (2)
/* #define DITHER_FLAG     (paDitherOff)  */
#define DITHER_FLAG     (0) /**/

/* Select sample format. */
#if 1
#define PA_SAMPLE_TYPE  paFloat32
typedef float SAMPLE;
#define SAMPLE_SILENCE  (0.0f)
#define PRINTF_S_FORMAT "%.8f"
#elif 1
#define PA_SAMPLE_TYPE  paInt16
typedef short SAMPLE;
#define SAMPLE_SILENCE  (0)
#define PRINTF_S_FORMAT "%d"
#elif 0
#define PA_SAMPLE_TYPE  paInt8
typedef char SAMPLE;
#define SAMPLE_SILENCE  (0)
#define PRINTF_S_FORMAT "%d"
#else
#define PA_SAMPLE_TYPE  paUInt8
typedef unsigned char SAMPLE;
#define SAMPLE_SILENCE  (128)
#define PRINTF_S_FORMAT "%d"
#endif

#define FORMATID "fmt "
#define DATAID   "data"

typedef struct {
  char    chunkID[4];
  long    chunkSize;
  short   wFormatTag;
  unsigned short wChannels;
  unsigned long dwSamplesPerSec;
  unsigned long dwAvgBytesPerSec;
  unsigned short wBlockAlign;
  unsigned short wBitsPerSample;
} FormatChunk;

typedef struct {
  char    chunkID[4];
  long    chunkSize;
} DataChunkHeader;



int checkHeader(FILE *fid) {

  char riff[4];
  char wave[4];

  fread(riff, 4, sizeof(char), fid);
  /* throwaway 4 bytes */
  fread(wave, 4, sizeof(char), fid);
  fread(wave, 4, sizeof(char), fid);

  if (!((strncmp(riff, "RIFF", 4) == 0) &&
       (strncmp(wave, "WAVE", 4) == 0))) {
    return -1;
  }
  
  return 0;
}


int getData(FILE *fid, char **data) {

  DataChunkHeader dch;
    
  while (strncmp(dch.chunkID, DATAID, 4) != 0) {
    fread(&dch, sizeof(DataChunkHeader), 1, fid);
    if (feof(fid) || ferror(fid))
      return -1;  
  }

  printf("Size of data: %d\n", dch.chunkSize);

  *data = (char *) malloc ( dch.chunkSize * sizeof(char) );
  fread(*data, sizeof(char), dch.chunkSize, fid);
  if (feof(fid) || ferror(fid)) {
    free(data);
    return -1;  
  }

  return dch.chunkSize;
}

int getFormatChunk(FILE *fid, FormatChunk *formatChunk) {
  
  while (strncmp(formatChunk->chunkID, FORMATID, 4) != 0) {
    fread(formatChunk, sizeof(FormatChunk), 1, fid);
    if (feof(fid) || ferror(fid))
      return -1;
  }
  return 0;
}



/*******************************************************************/
int main(int argc, char *argv[])
{
    PaStreamParameters outputParameters;
    PaStream *stream;
    PaError err;
    /*int i;
    int totalFrames;
    int numSamples;
    int numBytes;
    */
       
    /* read wave file */
    char *filename;
    FILE *fid;
    
    if (argc < 2) {
      printf("Usage: %s filename.wav\n", argv[0]);
      return -1;
    }
    
    /* filename */
    filename = argv[1];
    printf("Filename: %s\n", filename);
    
    /* open file */
    fid = fopen(filename, "rb");
    if (fid == NULL) {
      printf("Could not open file %s\n", filename);
      return -1;
    }
    
    /* check header */
    if (checkHeader(fid) < 0) {
      printf("Not a wave file!\n");
      return -1;
    }
    
    FormatChunk formatChunk;
    int data_size;
    char *data;

    if (getFormatChunk(fid, &formatChunk) < 0) {
      printf("Couldn't read header\n");
      return -1;
    }
    
    printf("Chunk Size       : %d\n", formatChunk.chunkSize);
    printf("Compressed       : %d\n", formatChunk.wFormatTag != 1);
    printf("Channels         : %d\n", formatChunk.wChannels);
    printf("SamplesPerSecond : %d\n", formatChunk.dwSamplesPerSec);
    printf("dwAvgBytesPerSec : %d\n", formatChunk.dwAvgBytesPerSec);
    printf("wBlockAlign      : %d\n", formatChunk.wBlockAlign);
    printf("wBitsPerSample   : %d\n", formatChunk.wBitsPerSample);
    
    if ((data_size = getData(fid, &data)) < 0) {
      printf("Couldn't read data\n");
      return -1;
    }
    
    int total_frames = data_size / formatChunk.wBlockAlign;

    printf("Total Frames     : %d\n", total_frames); 
    /* fclose(fid); */


    err = Pa_Initialize();
    if( err != paNoError ) goto error;

    /* Playback recorded data.  -------------------------------------------- */
    
    outputParameters.device = Pa_GetDefaultOutputDevice(); /* default output device */

    outputParameters.channelCount = formatChunk.wChannels;
    outputParameters.sampleFormat =  paInt16;

    outputParameters.suggestedLatency = Pa_GetDeviceInfo( outputParameters.device )->defaultLowOutputLatency;

    printf("YO YO\n"); fflush(stdout);
    outputParameters.hostApiSpecificStreamInfo = NULL;

    printf("Begin playback.\n"); fflush(stdout);
    err = Pa_OpenStream(
              &stream,
              NULL, /* no input */
              &outputParameters,
              formatChunk.dwSamplesPerSec,
              0, /*FRAMES_PER_BUFFER, */
              paClipOff,      /* we won't output out of range samples so don't bother clipping them */
              NULL, /* no callback, use blocking API */
              NULL ); /* no callback, so no callback userData */
    if( err != paNoError ) goto error;

    if( stream )
    {
        err = Pa_StartStream( stream );
        if( err != paNoError ) goto error;
        printf("Waiting for playback to finish.\n"); fflush(stdout);

        err = Pa_WriteStream( stream, data, total_frames );
        if( err != paNoError ) goto error;

        err = Pa_CloseStream( stream );
        if( err != paNoError ) goto error;
        printf("Done.\n"); fflush(stdout);
    }
    free( data );

    Pa_Terminate();
    return 0;

error:
    Pa_Terminate();
    fprintf( stderr, "An error occured while using the portaudio stream\n" );
    fprintf( stderr, "Error number: %d\n", err );
    fprintf( stderr, "Error message: %s\n", Pa_GetErrorText( err ) );
    return -1;
}

