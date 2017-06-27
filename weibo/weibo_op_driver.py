# -*- coding:utf-8 -*-
'''
Created on 2017年6月25日

@author: wycheng
'''
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import os
import weibo_api

class WBoperator:
#     driver = webdriver.PhantomJS(service_args=['--remote-debugger-port=9001'])# chrome浏览器驱动
    driver = webdriver.Chrome()# chrome浏览器驱动
    driver.implicitly_wait(10)# 设置隐性等待时间，等待页面加载完成才会进行下一步，最多等待10秒
    driver.set_window_size(1920, 1080)# 用phantomjs必须有这行
    wait=WebDriverWait(driver,10)
    uid_login=''
    
    # 根据验证框的存在与否判断是否要输入验证码
    def isVerifyCodeExist(self):
        try:# 如果成功找到验证码输入框返回true
            self.driver.find_element_by_css_selector('input[name="verifycode"]')
            return True
        except:# 如果异常返回false
            return False
    
    # 输入验证码部分，如果无需输入则直接返回，否则手动输入成功后返回        
    def inputVerifyCode(self):
        input_verifycode=self.driver.find_element_by_css_selector('input[name="verifycode"]')# 验证码输入框
        bt_change=self.driver.find_element_by_css_selector('img[action-type="btn_change_verifycode"]')# 验证码图片，点击切换
        bt_logoin=self.driver.find_element_by_class_name('login_btn')# 登录按钮
        while self.isVerifyCodeExist():
            print u'请输入验证码……(输入"c"切换验证码图片)'
            # 截屏以便手动输入验证码
            self.driver.save_screenshot('../screenshots/verifycode.jpg')
            verifycode=raw_input()
            if verifycode=='c':
                bt_change.click()
            else:
                input_verifycode.send_keys(verifycode)
                bt_logoin.click()
                # 点击完登录以后判断是否成功
                if self.driver.current_url.split('/')[-1]=='home':
                    print u'登录成功'
                    break
                else:
                    print u'输入的验证码不正确'
    
    # 打开微博首页进行登录的过程
    def login(self,account,password):
        
        url='http://weibo.com/'
        self.driver.get(url)
        
        # 输入账号密码并登录
        loginname=self.wait.until(lambda x:x.find_element_by_id('loginname'))
        loginname.send_keys(account)
        self.driver.find_element_by_css_selector('input[type="password"]').send_keys(password)
         
        bt_logoin=self.driver.find_element_by_class_name('login_btn')
        bt_logoin.click()
         
        # 如果存在验证码，则进入手动输入验证码过程
        if self.isVerifyCodeExist():
            self.inputVerifyCode()  
        
        # 登录成功以后读取用户昵称，调用api获取用户id
        username=self.driver.find_element_by_xpath('//a[@class="gn_name"]/em[2]').get_attribute('innerHTML')
        self.uid_login=weibo_api.getID(username)
        print self.uid_login
    # 上传文字
    def upload_txt(self,text):
        input_w=self.driver.find_element_by_xpath('//div[@node-type="textElDiv"]/textarea[@class="W_input"]')
        input_w.send_keys(text)
        sleep(1)
    
    #运行上传图片脚步
    def upload_img_script(self,time_bef,time_after,path):# path参数需要前后带双引号
        sleep(time_bef)# 等待弹窗时间
        os.system('C:/Users/15850/Documents/GitHub/MyWorkspace/py_study/script/upload.exe '+path)
        sleep(time_after)# 等待图片加载时间
        
    # 上传文字和单图
    def upload_txt_img(self,text,img_path):
        self.upload_txt(text)# 将文字上传
        img=self.driver.find_element_by_css_selector('a[action-type="multiimage"]')# 图片按钮
        img.click()# 点击图片按钮
        sleep(1)# 等待加载其他按钮
        
        #单图/多图按钮，即上传图片按钮
        bt_uploadimg=WebDriverWait(self.driver,10).until(lambda x:x.find_element_by_xpath('//object[contains(@id,"swf_upbtn")]'))
        bt_uploadimg.click()# 点击上传按钮
        
        self.upload_img_script(1,2,img_path)
    
    # 上传文字和多图    
    def upload_txt_multiImg(self,text,img_path_list):
        self.upload_txt_img(text,img_path_list[0])# 将文字和第一张图片上传
       
        len_imgs=len(img_path_list)# 图片地址list的长度    
        bt_uploadimg=WebDriverWait(self.driver,10).until(lambda x:x.find_element_by_xpath('//li[@node-type="uploadBtn"]/div/object[contains(@id,"swf_upbtn")]'))
        for i in range(len_imgs-1):# 将剩余图片上传 
            bt_uploadimg.click()
            self.upload_img_script(1, 2,img_path_list[i+1])
    
    # 发布
    def send(self):
        self.driver.find_element_by_class_name('W_btn_a').click()
        sleep(4)# 等待发送成功字样消失

    
    # 批量删除微博
    def delete(self,num):
        # 进入到微博列表页面
        self.driver.find_element_by_xpath('//strong[@node-type="weibo"]').click()
        sleep(1)
        for i in range(num):
            # 找到最新一条微博的下拉选项按钮
#             last_weibo=self.driver.find_element_by_xpath('//div[contains(@id,"Pl_Official_MyProfileFeed")]/div[@node-type="feed_list"]/div[2]')
            self.driver.find_element_by_xpath('//a[@action-type="fl_menu"]').click()
            self.driver.find_element_by_xpath('//a[@action-type="feed_list_delete"]').click()
            self.driver.find_element_by_xpath('//a[@action-type="ok"]').click()
            sleep(1)
    
    # 关注用户
    def follow(self,uid):
        self.driver.get('http://weibo.com/u/'+uid)
        focuslink=self.wait.until(lambda x:x.find_element_by_xpath('//div[@node-type="focusLink"]/a'))
        focuslink.click()
    
    # 批量关注（参数可能包含已关注用户和自身id）
    def follow_uidlist(self,uid_list):# 参数为uid的一个list
        for uid in uid_list:
            if uid==self.uid_login:# 如果是自己的id，跳过
                continue
            
            str_frship=weibo_api.getFriendship(self.uid_login, uid)
            if str_frship=='1:0' or str_frship=='1:1' :# 如果是已关注或者互相关注的用户，则跳过
                continue
            
            # 是未关注用户，则关注
            self.follow(uid)
    
    # 取消关注
    def unfollow(self,uid):
        self.driver.get('http://weibo.com/u/'+uid)
        focuslink=self.wait.until(lambda x:x.find_element_by_xpath('//div[@node-type="focusLink"]/a'))
        focuslink.click()
        sleep(0.5)
        cancel_attan=self.wait.until(lambda x:x.find_element_by_xpath('//a[@suda-data="key=tblog_profile_v6&value=cancel_atten"]'))
        cancel_attan.click()
        pass
operator=WBoperator()
operator.login('15850782585', 'Weibo6981228.')
#  15151892433,ZSMuYu104104

# path_list=[]
# for i in range(9):
#     path_list.append('"C:\\Users\\15850\\Documents\\GitHub\\MyWorkspace\\py_study\\img\\'+str(i+1)+'.jpg"')
# 
# upl=Uploader()
# upl.login('15850782585','Weibo6981228.')
# 
# upl.upload_txt(u'测试无图')
# upl.send()
# upl.upload_txt_img(u'测试单图',path_list[0])
# upl.send()
# upl.upload_txt_multiImg(u'测试9图',path_list)
# upl.send()