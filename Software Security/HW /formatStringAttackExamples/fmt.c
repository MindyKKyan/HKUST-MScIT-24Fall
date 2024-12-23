/* compiled using 
  gcc -O0 -fstack-protector -no-pie -z execstack fmt2633.c -o fmt2633
*/
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void noSecret(){
        /* 64 bit
        each %p prints 64-bit (quadword)
        0th - 5th are in rdi rsi rdx rcx r8 and r9
        6 th on the stack, and that's the address of answer[]
        answer[20] allocated 24 bytes (3 quadwords)
        6+3=9th argument is the canary, 
        canary 64-bit

       */
        char answer[24]="%6$p,%7$p,%8$p,%9$p";
	/*char input[20];*/

        /*printf("%p\n",answer);*/

	/*int secret = 22;*/

/*	gets(answer);*/
/*	printf("%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%12$p,%13$p,%14$p,%15$p,%16$p,%17$p,%18$p,%19$p,%20$p,%21$p\n",1,2,3,4,5,6,7,8,9,10,11);*/
        printf("%s",answer);

        /*printf("Do you like this course (yes/no)? \n");*/
        /*gets(answer);*/



}

int main(){

	noSecret();
	return 0;
}
