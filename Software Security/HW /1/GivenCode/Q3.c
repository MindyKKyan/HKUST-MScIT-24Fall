/* compiled using 
  gcc -m32 - fno-stack-protetor -z execstack bufferOverflow2.c -o bufferOverflow2
*/
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

void noSecret(){
        char answer[96];
        printf("%p\n",&answer);

        printf("Do you like this course (yes/no)? \n");
        gets(answer);

}

int main(){

	noSecret();
	return 0;
}
