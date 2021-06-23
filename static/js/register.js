let vm = new Vue({
    el: '#app',
    delimiters: ['[[',']]'],
    data: {
        // 接收参数
        username:'',
        password:'',
        password2:'',
        mobile:'',
        allow:'',
        uuid:'',
        image_code:'',
        image_code_url:'',
        sms_code:'',
        sms_code_tip: '获取短信验证码',
        sending_flag:false, // 避免重复点击发送短信按钮

        // 提示信息
        error_username:false,
        error_password:false,
        error_confirm:false,
        error_mobile:false,
        error_allow:false,
        error_image_code:false,
        error_sms_code: false,

        //
        error_username_message:'',
        error_password_message:'',
        error_confirm_message:'',
        error_mobile_message:'',
        error_captcha_message:'',
        error_allow_message:'',
        error_image_code_message:'',
        error_sms_code_message:'',


    },
    mounted:function (){
        this.generate_image_code()
    },
    methods: {
        // 获取短信验证码
        send_sms_code:function(){
            if(this.sending_flag == true){
                return;
            }
            this.sending_flag = true;
            this.check_mobile();
            this.check_image_code();
            if(this.error_mobile == true || this.error_image_code == true){
                this.sending_flag = false;
                return;
            }
            let url = "/sms_codes/" + this.mobile + "?image_code=" + this.image_code + "&" + "uuid=" + this.uuid
            // 短信验证码倒计时
            // 间隔指定的毫秒数不停地执行指定的代码，定时器
            axios.get(url).then(response=>{
                if(response.data.code == "0"){
                    let num = 60;
                    let t = setInterval(()=>{
                        // 如果发送成功，显示倒计时，隐藏点击图片按钮（用sending_flag来判断）
                            if(num == 1){
                                // 停止定时器
                                clearInterval(t);
                                this.sms_code_tip = "获取短信验证码";
                                this.sending_flag = false;
                            }else{
                                num -= 1;
                                this.sms_code_tip = num + "秒";
                            }
                    }, 1000, 60)
                }else{
                    if(response.data.code == '4001'){
                        this.error_image_code = true;
                        this.error_image_code_message = response.data.errmsg;
                    }else{
                        this.error_sms_code = true;
                        this.error_sms_code_message = response.data.errmsg;
                    }
                    this.generate_image_code();
                    this.sending_flag = false;
                    this.image_code = "";
                }
            }).catch(error=>{
                // 刷新发送验证码按钮
                console.log(error.response);
                this.sending_flag = false;
            });
        },
        // 生成图片验证码UUID
        generate_image_code() {
            this.uuid = generateUUID()
            this.image_code_url = "/image_code/" + this.uuid + "/"
        },
        // 检测用户名
        check_username:function () {
            let re = /^[a-zA-Z0-9_]{5,20}$/;
            if(re.test(this.username)){
                this.error_username=false;
                // 验证用户名是否重复
                let url = "/usernames/" + this.username + "/count/";
                axios.get(url).then(response=>{
                    if(response.data.count == 0){
                        this.error_username = false
                    }else{
                        this.error_username = true
                        this.error_username_message = '用户名已存在！'
                    }
                }).catch(error=>{
                    alert("验证用户名重复异常：" + error)
                })
            }else {
                this.error_username_message='请输入5-20个字符的用户';
                this.error_username=true;
            }
        },
        // 检测密码
        check_password:function () {
            let re = /^[a-zA-Z0-9]{8,20}$/;
            if(re.test(this.password)){
                this.error_password=false;
            }else {
                this.error_password_message='请输入8-20个字符密码';
                this.error_password=true;
            }
        },
        // 检测确认密码
        check_confirm_password:function () {
            if(this.password2 != this.password){
                this.error_confirm=true;
                this.error_confirm_message='两次输入的密码不一致'
            }else{
                this.error_confirm=false;
            }
        },
        // 检测图形验证码
        check_image_code:function () {
            let re = /^[a-zA-Z0-9]{4}$/;
            if(re.test(this.image_code)){
                this.error_image_code=false;
            }else {
                this.error_image_code_message='请输入正确的验证码';
                this.error_image_code=true;
            }
        },
        // 检测手机号
        check_mobile:function () {
            let re = /^1[3-9]\d{9}$/;
            if(re.test(this.mobile)){
                this.error_mobile=false;
            // 验证手机号是否重复
                let url = "/mobile/" + this.mobile + "/count/"
                axios.get(url).then(response=>{
                    if(response.data.count == 0){
                        this.error_mobile = false
                    }else{
                        this.error_mobile_message = '手机号已注册'
                        this.error_mobile = true
                    }
                }).catch(error=>{
                    alert(error.data.errmsg)
                })
            }else{
                this.error_mobile=true;
                this.error_mobile_message='请输入正确的手机号码';
            }
        },
        // 检测短信验证码
        check_sms_code:function (){
            let re = /^\d{6}$/
            if(re.test(this.sms_code)){
                this.error_sms_code = false
            }else{
                this.error_sms_code_message = '请输入正确的短信验证码'
                this.error_sms_code = true
            }
        },
        // 提交注册按钮
        on_submit:function () {

            this.check_username();
            this.check_password();
            this.check_confirm_password();
            this.check_mobile();

            if(this.error_username==true||this.error_password==true||this.error_confirm==true||this.error_mobile==true){
                window.event.returnValue=false;
            }
        },

    },
})