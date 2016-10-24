# 部署spark on yarn集群模式

持续大半个月，断断续续，走走停停，终于还是搭好这套集群并测试成功，心戚戚然，赶紧复盘一下。

忽略背景介绍，其实我也不太知道spark到底能做什么事，边走边看

## 系统配置
* 系统：centos6.4
* 配置：4核-6G-？G（内存还是高点吧，我一开始使用1G内存，坑死自己了）
* 数量：3台（要不怎么叫集群咧）

## 前期准备
* 设置hostname（/etc/sysconfig/network），详略；
* 绑定主机名和对应ip（/etc/hosts），详略；
  * 172.16.60.218 master
  * 172.16.60.219 slave1  
  * 172.16.60.220 slave2
* ssh无密码登陆，详略；
* 关闭防火墙
 * `service iptables stop`
 * `chkconfig iptables off`
* 关闭selinux
 * `setenforce 0`

## 统一的工作目录
* /root/work

## 安装java
一般会先卸载掉系统默认的openjdk，使用从java官网下载的jdk。我下载的是jdk-8u91-linux-x64.rpm。hadoop的版本需要jdk6以上。
```
rpm -ivh /root/work/jdk-8u91-linux-x64.rpm
```

修改环境变量，~/.bashrc和/etc/profile都会添加，文件末添加：
```
#java env
export JAVA_HOME=/usr/java/jdk1.8.0_91/
export JRE_HOME=/usr/java/jdk1.8.0_91/jre
export PATH=$PATH:$JAVA_HOME/bin:$JAVA_HOME/sbin
export CLASSPATH=.:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar:$JRE_HOME/lib
```
验证java版本
```
[root@master work]# source ~/.bashrc /etc/profile #使环境变量生效
[root@master work]# java -version                 #查看java版本
java version "1.8.0_91"
Java(TM) SE Runtime Environment (build 1.8.0_91-b14)
Java HotSpot(TM) 64-Bit Server VM (build 25.91-b14, mixed mode)
```

在各个slave重复以上java部署，略。

## 安装Scala（可选）
spark官方需要scala2.10.x以上，我这里使用scala-2.10.3，从sacla官方[下载](http://www.scala-lang.org/download/all.html).
```
tar zvxf /root/work/scala-2.11.8.tgz

```
修改环境变量，~/.bashrc和/etc/profile都会添加，文件末添加：
```
#scala env
export SCALA_HOME=$WORK_SPACE/scala-2.10.3
export PATH=$PATH:$SCALA_HOME/bin
```
并验证 scala 是否安装成功
```
[root@master work]# source ~/.bashrc /etc/profile #使环境变量生效
[root@master work]# scala -version                #验证是否生效
Scala code runner version 2.10.3 -- Copyright 2002-2013, LAMP/EPFL
```
在各个slave重复以上java部署，略。

`注：预编译的二进制包已包含scala运行环境，不需要另外安装Scala便可运行Spark`

##  安装配置 Hadoop YARN
####  下载解压
从[hadoop官网下载](https://archive.apache.org/dist/hadoop/common/)，我下载的是hadoop-2.6.0。
```
tar zvxf /root/work/hadoop-2.6.0.tar.gz
```
####  配置 Hadoop
`cd /root/work/hadoop-2.6.0/etc/hadoop`进入hadoop配置目录，需要配置有以下文件

* `yarn-env.sh`
* `slaves`
* `core-site.xml`
* `hdfs-site.xml`
* `maprd-site.xml`
* `yarn-site.xml`

1、文件 **slaves**，将作为 DataNode 的主机名写入该文件，每行一个，默认为 localhost，所以在伪分布式配置时，节点即作为 NameNode 也作为 DataNode。分布式配置可以保留 localhost，也可以删掉，此处，我保留master也作为DataNode。
```
master
slave1
slave2
```
2、**core-site.xml**文件，/root/work/hadoop-2.6.0/tmp，需要手动创建。
```
<configuration>
        <property>
                <name>fs.defaultFS</name>
                <value>hdfs://master:9000</value>
        </property>
        <property>
                <name>hadoop.tmp.dir</name>
                <value>file:/root/work/hadoop-2.6.0/tmp</value>
                <description>Abase for other temporary directories.</description>
        </property>
</configuration>
```
创建tmp文件
```
mkdir /root/work/hadoop-2.6.0/tmp
```
3、**hdfs-site.xml**文件，dfs.replication 一般设为 3，但我们只有2个 Slave 节点，所以 dfs.replication 的值还是设为 2：
```
<configuration>
        <property>
                <name>dfs.namenode.secondary.http-address</name>
                <value>master:50090</value>
        </property>
        <property>
                <name>dfs.replication</name>
                <value>2</value>
        </property>
        <property>
                <name>dfs.namenode.name.dir</name>
                <value>file:/root/work/hadoop-2.6.0/tmp/dfs/name</value>
        </property>
        <property>
                <name>dfs.datanode.data.dir</name>
                <value>file:/root/work/hadoop-2.6.0/tmp/dfs/data</value>
        </property>
</configuration>
```

4、文件 **mapred-site.xml** （可能需要先重命名，默认文件名为 mapred-site.xml.template），然后配置修改如下：
```
<configuration>
        <property>
                <name>mapreduce.framework.name</name>
                <value>yarn</value>
        </property>
        <property>
                <name>mapreduce.jobhistory.address</name>
                <value>master:10020</value>
        </property>
        <property>
                <name>mapreduce.jobhistory.webapp.address</name>
                <value>master:19888</value>
        </property>
</configuration>
```

5、文件 **yarn-site.xml**：
```
<configuration>
        <property>
                <name>yarn.resourcemanager.hostname</name>
                <value>master</value>
        </property>
        <property>
                <name>yarn.nodemanager.aux-services</name>
                <value>mapreduce_shuffle</value>
        </property>
</configuration>
```
6、**yarn-env.sh**文件末添加：
```
export JAVA_HOME=/usr/java/jdk1.8.0_91/
```

#### 复制到各个slave
```
scp -r /root/work/hadoop-2.6.0 slave1:/root/work/
scp -r /root/work/hadoop-2.6.0 slave2:/root/work/
```
#### hadoop初始化
首次启动需要先在 Master 节点执行 NameNode 的格式化:
```
cd /root/work//hadoop-2.6.0/bin/
hdfs namenode -format       # 首次运行需要执行初始化，之后不需要
```
完成后，启动hadoop：
```
cd /root/work//hadoop-2.6.0/sbin/
./start-all.sh
```
通过命令 `jps` 可以查看各个节点所启动的进程。正确的话，在 Master 节点上可以看到进程:
```
[root@master hadoop]# jps
4116 Worker
1925 ResourceManager
1766 SecondaryNameNode
1479 NameNode
1607 DataNode
5131 Jps
2127 NodeManager
```

在 Slave 节点可以看到 DataNode 和 NodeManager 进程，如下图所示：
```
[root@slave2 ~]# jps
1542 NodeManager
2380 Worker
2621 Jps
1438 DataNode
```

也可以通过 Web 页面看到查看 DataNode 和 NameNode 的状态：[http://master:50070/](http://master:50070/)。如果不成功，可以通过启动日志排查原因。


## 部署Spark
#### 下载
进入[spark官方下载地址](http://spark.apache.org/downloads.html),注意选择的对应的hadoop的版本。比如我的hadoop是2.6.0，那么我选择的是spark-2.0.0-bin-hadoop2.6.tgz

```
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.0.0-bin-hadoop2.6.tgz
```

#### 解压
```
tar zvxf  /root/work/spark-2.0.0-bin-hadoop2.6.tgz
```

#### 配置 Spark
```
cd /root/work/spark-2.0.0/conf/
cp spark-env.sh.template spark-env.sh
```

1、添加以下信息到spark-env.sh
```
export SCALA_HOME=/root/work/scala-2.10.3
export JAVA_HOME=/usr/java/jdk1.8.0_91/
export HADOOP_HOME=/root/work/hadoop-2.6.0
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
SPARK_MASTER_IP=master
SPARK_LOCAL_DIRS=/root/work/spark-2.0.0
SPARK_DRIVER_MEMORY=5G
```
注：在设置Worker进程的CPU个数和内存大小，要注意机器的实际硬件条件，如果配置的超过当前Worker节点的硬件条件，Worker进程会启动失败，但内存也别设太小了，别小于1G。

2、添加以下信息到slaves：
```
master
slave1
slave2
```

将配置好的spark-2.0.0文件夹分发到各个salve
```
scp -r /root/work/spark-2.0.0/ slave1:/root/work
scp -r /root/work/spark-2.0.0/ slave2:/root/work
```

#### 启动Spark
```
cd /root/work/spark-2.0.0/sbin/
./start-all.sh
```

#### 验证 Spark 是否安装成功

用`jps`检查，在 master 上应该有以下几个进程：
```
[root@master sbin]# jps
4116 Worker
8260 Jps
4021 Master
```

进入Spark的Web管理页面： [http://master:8080](http://master:8080/)


####備忘紀事

* spark參數設置
 
```
#以下兩者皆需填入
spark.driver.memory
spark.executor.memory → 代表每個執行機所可使用的內存量 
```

* python環境提醒
  三台環境需配置一樣，包含python版本，因為同步版本出現無法運行的錯誤

  
* 添加環境變量：vim /home/root/profile

```
export WORK_SPACE=/root/work/
#java env
export JAVA_HOME=/usr/java/jdk1.8.0_91/
export JRE_HOME=/usr/java/jdk1.8.0_91/jre
export PATH=$PATH:$JAVA_HOME/bin:$JAVA_HOME/sbin
export CLASSPATH=.:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/lib/dt.jar:$JRE_HOME/lib

#hadoop env
export HADOOP_HOME=/root/work/hadoop-2.6.0
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
#spark env
export SPARK_HOME=/root/work/spark-2.0.0
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

```

---
## CHANGELOG
20160819 零丁创建
