##hdfs 简易操作指南说明

將一些會使用到的指令做個小記錄

#文件的操作

* 導入導出
``` 
文件導入
hadoop fs -put <local-src> ... <HDFS_dest_path>
hadoop fs -put popularNames.txt /user/hadoop/dir1/popularNames.txt
```
```
文件導出
hadoop fs -get <hdfs_src> <localdst># Example
hadoop fs -get /user/hadoop/dir1/popularNames.txt /home/
```
* 創建文件夾
```
hadoop fs -mkdir <paths>
hadoop fs -mkdir /user/hadoop
hadoop fs -mkdir /user/hadoop/dir1 /user/hadoop/dir2 /user/hadoop/dir3
```
