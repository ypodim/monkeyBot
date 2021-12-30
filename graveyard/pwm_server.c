#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h> //memset
#include <arpa/inet.h>
#include <sys/socket.h>
#include <pigpio.h> 

#define PORT 8888   //The port on which to listen for incoming data
#define BUFSIZE 512

/*
gcc -Wall -pthread -o pwm_server pwm_server.c -lpigpio

sudo ./servo_demo          # Send servo pulses to GPIO 4.
sudo ./servo_demo 23 24 25 # Send servo pulses to GPIO 23, 24, 25.
*/

#define NUM_GPIO 32

#define MIN_WIDTH 630
#define MAX_WIDTH 2410

int run=1;

int width[NUM_GPIO];

void stop(int signum) {
   run = 0;
}

int cleanup() {
   printf("tidying up\n");
   gpioTerminate();
   return 0;
}

int getSocket() {
   struct sockaddr_in myaddr;
   int fd;

   if ((fd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
      perror("cannot create socket\n");
      return 0;
   }

   memset((char *)&myaddr, 0, sizeof(myaddr));
   myaddr.sin_family = AF_INET;
   myaddr.sin_addr.s_addr = htonl(INADDR_ANY);
   myaddr.sin_port = htons(PORT);

   if (bind(fd, (struct sockaddr *)&myaddr, sizeof(myaddr)) < 0) {
      perror("bind failed");
      return 0;
   }

   return fd;
}

void pwm(int gpio, int pulse) {
   pulse = pulse<MIN_WIDTH ? MIN_WIDTH : pulse;
   pulse = pulse>MAX_WIDTH ? MAX_WIDTH : pulse;
   printf("pin: %d, pulse: %d\n", gpio, pulse);
   
   gpioServo(gpio, pulse);
   // int prevPulse = width[gpio];
   // for (; prevPulse!=pulse; prevPulse+= prevPulse<pulse ? 1 : -1) {
   //    gpioServo(gpio, prevPulse);
   //    time_sleep(0.003);
   // }
   width[gpio] = pulse;
}

int main(int argc, char *argv[]) {
   int g;
   int fd;

   if (gpioInitialise() < 0) return -1;
   gpioSetSignalFunc(SIGINT, stop);

   for (g=0; g<NUM_GPIO; g++) {
      width[g] = (MIN_WIDTH + MAX_WIDTH)/2;
   }

   if ((fd=getSocket()) == 0) {
      perror("cannot create socket\n");
      return 0;
   }

   char buf[BUFSIZE];
   struct sockaddr_in remaddr;
   socklen_t addrlen = sizeof(remaddr);

   while (run) {
      printf("waiting for data...\n");
      int recvlen = recvfrom(fd, buf, BUFSIZE, 0, (struct sockaddr *)&remaddr, &addrlen);
      if (recvlen == 5) {
         int pin = buf[0] - 48; //ascii '0' = 48
         buf[recvlen] = 0;
         if (pin >= 0 && pin < 41)
            pwm(pin, atoi(buf+1));
         else
            printf("got bad data: %s\n", buf);   
      } else {
         printf("got bad data length: %s\n", buf);
      }
   }
   return cleanup();
}
