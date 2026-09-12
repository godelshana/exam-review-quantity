var common = {
    isCheckLogin:function isCheckLogin(is_login){
        if(is_login==0){
            common.layerOpen(2,1,'365px','432px','/Pc/Login/mobile_login');
            return false;
        }else{
            return true;
        }
    },
    layerOpen:function layerOpen(type=2,closeBtn=1,layer_width,layer_height,url=''){
        layui.use('layer', function() {
            layer.open({
                id:'video-layer',
                type:type,
                closeBtn: closeBtn,
                area: [layer_width, layer_height],
                title:false,
                scrollbar:false,
                shade: [0.5, '#000'],
                shadeClose:true,
                content:url,
                success: function(layero, index){},
                cancel:function(index){
                    layer.closeAll();
                }
            });
        });
        return false;
    },
    mobileIsCheckLogin:function mobileIsCheckLogin(is_login){
        if(is_login==0){
            common.mobileLayerOpen(1,1,'80%','15rem');
            return false;
        }else{
            return true;
        }
    },
    mobileLayerOpen:function mobileLayerOpen(type=2,closeBtn=1,layer_width,layer_height,url=''){
        layui.use('layer', function() {
            layer.open({
                id:'share-layer',
                type:type,
                closeBtn: closeBtn,
                area: [layer_width, layer_height],
                title:false,
                scrollbar:false,
                shade: [0.5, '#000'],
                shadeClose:true,
                content:'<div class="login">\n' +
                            '<div class="login-mobile"><input  type="text" name="mobile" id="mobile" value="" placeholder="请输入手机号" maxlength="11"/></div>\n' +
                            '<div class="login-verify"><input  type="text" name="code" value="" id="code" required autocomplete="off" placeholder="请输入验证码"/>' +
                                '<input type="button" id="yzm"  style="width: 5rem!important;color:#FF6B2E;background-color: #fff;float:right; border-radius: 1rem border: 1px solid #FF6B2E!important" value="发送验证码" maxlength="6"></div>\n' +
                            '<div class="login-button" ><button id="loginBtn">登 录</button></div>\n' +
                        '</div>',
                success: function(layero, index){},
                cancel:function(index){
                    layer.closeAll();
                }
            });
        });
    }
}

var studyTime = {
    subject_id:null,
    id:null,
    type_id:null,
    watch_time:0,
    current_time:0,
    last_update_time:0,
    addCourse:function (course_id,chapter_id,video_type,total_time,start_time,func=function () {}) {
        $.ajax({
            type: "POST",
            url:  "/pc/studyTime/add",
            data: {
                type:1,
                type_id:course_id,
                type_id_param:chapter_id,
                video_type:video_type,
                total_time:total_time,
                start_time:start_time,
            },
            dataType:'json',
            success: function (resule) {
                if(resule.status==1){
                    studyTime.id = resule.data.id;
                    studyTime.createInterval();
                    func();
                    console.log('学习记录添加成功id:'+resule.data.id)
                }else{
                    console.log('学习记录添加失败')
                }
            },
        });
    },
    addXingQuestion:function (report_id,is_analysis,func=function () {}) {
        let type;
        studyTime.type_id = report_id;
        if(is_analysis!=1){
            type = 2;
        }else {
            type = 4;
        }
        $.ajax({
            type: "POST",
            url:  "/pc/studyTime/add",
            data: {
                type:type,
                type_id:report_id,
                subject_id:studyTime.subject_id
            },
            dataType:'json',
            success: function (resule) {
                if(resule.status==1){
                    studyTime.id = resule.data.id;
                    studyTime.createInterval();
                    func();
                    console.log('学习记录添加成功id:'+resule.data.id)
                }else{
                    console.log('学习记录添加失败')
                }
            },
        });
    },
    addShenQuestion:function (report_id,is_analysis,func=function () {}) {
        let type;
        studyTime.type_id = report_id;
        if(is_analysis!=1){
            type = 3;
        }else {
            type = 5;
        }
        $.ajax({
            type: "POST",
            url:  "/pc/studyTime/add",
            data: {
                type:type,
                type_id:report_id,
                subject_id:studyTime.subject_id
            },
            dataType:'json',
            success: function (resule) {
                if(resule.status==1){
                    studyTime.id = resule.data.id;
                    studyTime.createInterval();
                    func();
                    console.log('学习记录添加成功id:'+resule.data.id)
                }else{
                    console.log('学习记录添加失败')
                }
            },
        });
    },
    update:function () {
        if(studyTime.id==null){
            return false;
        }
        let tmp = studyTime.watch_time;
        studyTime.last_update_time = studyTime.watch_time;
        $.ajax({
            type: "POST",
            url:  "/pc/studyTime/update",
            data: {
                id:studyTime.id,
                watch_time:studyTime.watch_time,
                current_time:studyTime.current_time,
                type_id:studyTime.type_id
            },
            dataType:'json',
            success: function (resule) {
                if(resule.status==1){
                    console.log('学习记录更新成功')
                }else{
                    console.log('学习记录更新失败')
                }
            },
        });
    },
    createInterval:function (fun=function () {}) {
        setInterval(function () {
            studyTime.watch_time++;
            if((studyTime.watch_time - studyTime.last_update_time)>= 60){
                studyTime.update()
            }
            fun();
        },1000);
    }
}