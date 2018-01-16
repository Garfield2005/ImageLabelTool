## 图片标注工具

> version: 1.0.0  
> author: zhangmm  
> create date: 01/16 2018  
> email: jolly.ming2005@gmail.com  

## Description
1. 用来对制定的图像集合进行标注
2. 目前只支持jpg格式图片
3. 提供python源码，同时提供了一个生成的exe文件可以在windows上使用(不依赖python环境)

## 格式要求
1. 待标注的图片目录结构:
 
    ```
    F:\data
    ├─dog
    │   dog-1.jpg
    │   dog-2.jpg
    │   dog-3.jpg
    │      
    └─cat
        cat-1.jpg
        cat-2.jpg
        cat-3.jpg
        cat-4.jpg
        cat-5.jpg
    ```

    - F:\data: 为数据集根目录
    - dog和cat: 为数据集名称名录
    - *.jpg: 为待标注图片

2. 输出格式

    ```
    F:\labelinfo
    ├─dog
    │   dog-1.txt
    │   dog-2.txt
    │   dog-3.txt
    │      
    └─cat
        cat-1.txt
        cat-2.txt
        cat-3.txt
        cat-4.txt
        cat-5.txt
    ```

    - F:\labelinfo: 为标注结果存储根目录
    - dog和cat： 标注结果存储子目录，和数据集目录相对应
    - *.txt: 标注结果信息

3. 标注结果格式（以dog-1.txt为例，即dog-1.jpg的标注结果）
   ```
   3
   dog	dog-1.jpg	349 30 132 167
   dog	dog-1.jpg	34 100 102 154
   dog	dog-1.jpg	134 300 60 80
   ```
   - 第一行数字：3表示dog-1.jpg共有三个标注结果(如标注了3个狗头)
   - 后续每行代表一个标注信息：第一列为类别(dog类或者cat类)；第二列为图片名称；第三列(四个数字)为标注区域
   - 标注区域格式：（x, y, width, height）

## 使用方法
1. 如果从源码运行，则直接运行ImageLabel.py文件即可：python ImageLabel.py
2. 如果在windows下运行exe程序，则直接下载ImageLabel.exe运行即可(需要同目录下Examples)
3. 在"Image/Label Dir"文本框中输入标注信息的存储目录，然后点击"SaveDirConfig"按钮确认
4. 在"Image/Label Dir"文本框中输入待标注的图片根目录(如本文档示例中的F:\data, 不能包括dog或者cat目录)，然后点击"Load"按钮载入图片
5. 图片载入后使用鼠标在标注区域框选(可选择多个区域)，点击"next\save"按钮保存当前标注信息，同时继续标注下一张

[](ImageLabelUsage.jpg)
