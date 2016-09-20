##  step1:preprocess 
class PreProcess():
    
    def __init__(self,sc,path):
        self.path = path
        
    def get_file():
        pass
    
    def merge():
        pass 
    
class PreLocal(PreProcess):
    
    def get_file(self):
        fnames = os.listdir(self.path)
        for f in fnames:
            if not re.search(".tar.gz", str(f)):
                yield  self.path+f+"/export/data/log_01/logs/"+f.split("_")[0]+"/world2.bi"   
                
    def merge(self):
        flag = 1
        for name in self.get_file():
            if flag==0:
                log = sc.textFile(name)
                logs = logs.union(log)
            if flag==1:
                logs = sc.textFile(name)
                flag = 0
        return logs
    
class PreHdfs(PreProcess):
    pass


## step2:filter
class Filter():
    def __init__(self,sc,log,*arg):
        self.sc = sc
        self.filter_key = arg
        self.log = log
    
    def partition(self):
        pass

class FMode1(Filter):
    def partition(self):
        for keys in self.filter_key:
            for key in keys:
                yield self.log.filter(lambda x : key in x)  

## step3:convert to json                
class Convert():
    def __init__(self,sc,logs,keys):
        self.sc = sc
        self.logs = logs
        self.keys = keys
        
    def tojson(self):
        #print(self.keys)
        for log,key in zip(self.logs,self.keys):
            locals()[key] = []
            for row in log.collect():
                word = []
                for text in row.split("|"):
                    word.append(text)
                locals()[key].append(word)
            yield locals()[key]
        

## step4:save to local file
class Save():
    pass


path = "F:/付費玩家資料/研究/data/日誌/靈狐/bi/"
key = ["usercreate","userlogin"]
#key = ["usercreate"]
step1 = PreLocal(sc,path)
step2 = FMode1(sc,step1.merge(),key).partition()
step3 = Convert(sc,step2,key).tojson()

#for i in step2.partition():
    #print(i.count())