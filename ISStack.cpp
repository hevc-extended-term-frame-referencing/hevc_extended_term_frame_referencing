#include <sys/resource.h>
#include <stdio.h>

int main (int argc, char **argv)
{
    const rlim_t kStackSize = 64L * 1024L * 1024L;   // min stack size = 64 Mb
    struct rlimit rl;
    int result;

    result = getrlimit(RLIMIT_STACK, &rl);
    if (result == 0)
    {
        printf("\nCurrent Stack size is %lld\n",(long long) rl.rlim_cur);
        if (rl.rlim_cur < kStackSize)
        {
            rl.rlim_cur = kStackSize;
            result = setrlimit(RLIMIT_STACK, &rl);
            if (result != 0)
            {
                fprintf(stderr, "setrlimit returned result = %d\n", result);
            }
        }
        result = getrlimit(RLIMIT_STACK, &rl);
        printf("\nNew Stack size is %lld\n",(long long) rl.rlim_cur);
    }

    // ...

    return 0;
}
