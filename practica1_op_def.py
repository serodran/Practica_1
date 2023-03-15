from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
import random


N = 5
NPROD = 4


def delay(factor = 3):
    sleep(3/factor)


def producer(buffer, sem_empty,sem_non_empty,pos,indice):

    cota_m=1
    for i in range(N):
        sem_empty.acquire()
        try:
            new_num=random.randint(cota_m, 10*(i+2))
            buffer[i] = new_num
            print (f"Productor {pos} produce {new_num}\n")
            delay(6)
            indice.value += 1
            cota_m=new_num
        finally:
            sem_non_empty.release()
    sem_empty.acquire()
    buffer[i]=-1
    sem_non_empty.release()



def get_data(buffer, l_indices):

    fin=0
    l=[]
    for i in range(NPROD):
        if l_indices[i]<N:
            if buffer[i][l_indices[i]]>=0:
                l.append((buffer[i][l_indices[i]],i))
    if l!=[]:
        aux=l[0]
        for j in l:
            if j[0]<aux[0]:
                aux = j
        data=aux
        l_indices[data[1]] = l_indices[data[1]]+1
    else:
        data=-1
        fin=1
    delay(6)
    #print(data)
    return (data,fin)



def consumer(buffer,buffer_final,sem_empty,sem_non_empty,l_indices):
    for i in range(NPROD):
        sem_non_empty[i].acquire()
    fin=0
    while fin==0:
        (dato,fin) =get_data(buffer, l_indices)
        if fin!=1:
            sem_empty[dato[1]].release()
            buffer[dato[1]][0]=-2
            buffer_final.append(dato[0])
            delay(6)
            print (f"El consumidor escoge {dato[0]} producido por {dato[1]}\n")
            sem_non_empty[dato[1]].acquire()
    print(buffer_final)
       

def main():
    indice = Value('i', 0)
    l_indices=[0]*NPROD

    buffer = [Array('i', N) for _ in range(NPROD)]
    for i in range(NPROD):
        for j in range(N):
            buffer[i][j]=-2
    sem_empty = [Semaphore(1) for i in range(NPROD)]
    sem_non_empty= [Semaphore(0) for i in range(NPROD)]
    buffer_final=[]
    prods = [Process(target=producer, args=(buffer[i],sem_empty[i],sem_non_empty[i],i,indice))
               for i in range(NPROD)]

    consum = Process(target=consumer,args=(buffer,buffer_final,sem_empty,sem_non_empty,l_indices))

    for p in prods:
        p.start()
       
    consum.start()

    for p in prods:
        p.join()
       
    consum.join()
   
if __name__ == '__main__':
    main()