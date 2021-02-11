from multiprocessing import Process

class dumb(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def run(self):
        print("I ran!")

if __name__ == "__main__":
    d = dumb()
    d.start()
    d.join()