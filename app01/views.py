from django.shortcuts import render
from django.http import JsonResponse
from app01 import models
import json
def index(request):
    time_choices = models.Book.time_choices
    response = render(request,'index.html',{'time_choices':time_choices})
    # response.set_signed_cookie(salt="sadf")
    # response.set_cookie()
    return response

def booking(reqeust):
    if reqeust.method == "GET":
        response = {'status':True,'msg':None,'data':None}
        try:
            import datetime
            current_date = datetime.datetime.now().date()
            choice_date = reqeust.GET.get('choice_date')
            choice_date = datetime.datetime.strptime(choice_date, '%Y-%m-%d').date()

            if choice_date < current_date:
                raise Exception('日期必须大于等于当前')
            # # ######################### 获取预定信息 ##################
            """
            booking_dict= {
                    4:{
                        5: {'name':'骚东','id':2}
                        6: {'name':'骚东','id':2}
                    },
                }
            """
            booking_list = models.Book.objects.filter(date=choice_date)
            booking_dict = {}
            for item in booking_list:
                if item.room_id not in booking_dict:
                    booking_dict[item.room_id] = {item.time_id: {'name': item.user.user, 'id': item.user_id}}
                else:
                    booking_dict[item.room_id][item.time_id] = {'name': item.user.user, 'id': item.user_id}

            # ############ 生成会议室信息 #################
            booking_info = []

            room_list = models.Room.objects.all()

            for room in room_list:
                td_list = [{'text':room.caption,'attrs':{}}, ]
                for tm in models.Book.time_choices:
                    if room.id in booking_dict and tm[0] in booking_dict[room.id]:
                        # 已预定
                        user_info = booking_dict[room.id][tm[0]]
                        #if user_info == request.session['xxxxx']['id']:
                        # 登录用户1，少尉
                        # 登录用户2，海东
                        if user_info['id'] == 2:
                            # 自己预定
                            print(room.id, room.caption, tm[0], tm[1], user_info['name'])
                            td_list.append({'text': '自己预定', 'attrs': {'class':'chosen','room_id':room.id,'time_id':tm[0]}})
                        else:
                            # 别人预定
                            print(room.id, room.caption, tm[0], tm[1], user_info['name'], 'disabled')
                            td_list.append({'text': user_info['name'], 'attrs': {'room_id':room.id,'time_id':tm[0],'class':'chosen','fuck':'true'},})

                    else:
                        td_list.append({'text':'','attrs':{ 'room_id':room.id,'time_id':tm[0] }})

                booking_info.append(td_list)
            response['data'] = booking_info
        except Exception as e:
            response['status'] = False
            response['msg'] = str(e)
        return JsonResponse(response)
    else:
        response = {'status': True, 'msg': None, 'data': None}
        try:
            import datetime
            current_date = datetime.datetime.now().date()
            choice_date = reqeust.POST.get('date')
            choice_date = datetime.datetime.strptime(choice_date, '%Y-%m-%d').date()
            if choice_date < current_date:
                raise Exception('日期必须大于等于当前')


            post_data = json.loads(reqeust.POST.get('data'))
            # {'DEL': {'4': ['5','6'],'7':[1,2]}, 'ADD': {'1': ['2', '3'], '2': ['3'], '4': ['5']}}
            for room_id,time_list in post_data['DEL'].items():
                if room_id not in post_data['ADD']:
                    continue
                for time_id in list(time_list):
                    if time_id in post_data['ADD'][room_id]:
                        post_data['ADD'][room_id].remove(time_id)
                        post_data['DEL'][room_id].remove(time_id)

            # 增加预定
            book_obj_list = []
            for room_id,time_list in post_data['ADD'].items():
                for time_id in time_list:
                    # models.Book.objects.create(room_id=room_id,time_id=time_id,user_id=2,date=choice_date)
                    obj = models.Book(room_id=room_id, time_id=time_id, user_id=2, date=choice_date)
                    book_obj_list.append(obj)
            models.Book.objects.bulk_create(book_obj_list)

            # 删除会议室预定信息
            from django.db.models import Q
            remove_booking = Q()
            for room_id, time_id_list in post_data['DEL'].items():
                for time_id in time_id_list:
                    temp = Q()
                    temp.connector = 'AND'
                    temp.children.append(('user_id',2,))
                    temp.children.append(('date', choice_date))
                    temp.children.append(('room_id', room_id,))
                    temp.children.append(('time_id', time_id,))

                    remove_booking.add(temp, 'OR')
            if remove_booking:
                models.Book.objects.filter(remove_booking).delete()
        except Exception as e:
            response['status'] = False
            response['msg'] = str(e)

        return JsonResponse(response)