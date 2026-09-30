import os,base64
import gradio as gr
BASE=os.path.dirname(os.path.abspath(__file__))
LOGO_PATH=os.path.join(BASE,'assets','logo.png'); FAVICON_PATH=os.path.join(BASE,'assets','favicon.png')
def _b64(p):
    with open(p,'rb') as f: return base64.b64encode(f.read()).decode()
LOGO_B64=_b64(LOGO_PATH)
HEADER_HTML=f'<div class="brand"><img src="data:image/png;base64,{LOGO_B64}" alt="شعار جامعة البطانة"><h1>نظام إدارة خريجي جامعة البطانة</h1><p>University of Al-Butana — Graduates Management System</p></div>'
LOGIN_LOGO=f'<div class="brand small"><img src="data:image/png;base64,{LOGO_B64}" alt="شعار"></div>'
from data import COLUMNS
from functions import *

CSS='''
html,body{direction:rtl}
.gradio-container{max-width:1450px!important;margin:auto!important;direction:rtl;text-align:right;padding:12px!important}
.gradio-container *{box-sizing:border-box}
.title{text-align:center}
.card{text-align:center;padding:15px;border-radius:14px}
.brand{text-align:center;padding:8px 0 4px}
.brand img{width:130px;height:auto;margin:0 auto;display:block}
.brand.small img{width:90px}
.brand h1{margin:8px 0 2px;color:#1b6b2f;line-height:1.4}
.brand p{margin:0;color:#666;direction:ltr}
/* حقول وأزرار مناسبة للمس (16px تمنع تكبير iOS التلقائي) */
.gradio-container input,.gradio-container textarea,.gradio-container select{font-size:16px!important}
.gradio-container button{min-height:44px}
/* الصفوف تلتف حسب عرض الشاشة */
.gradio-container .row{flex-wrap:wrap!important;gap:10px}
.gradio-container .row>*{min-width:220px!important;flex:1 1 220px!important}
/* الجداول: تمرير أفقي داخلها دون كسر الصفحة */
.gradio-container .table-wrap,.gradio-container [class*="dataframe"]{overflow-x:auto!important;max-width:100%}
/* شريط التبويبات قابل للتمرير */
.gradio-container [role="tablist"],.gradio-container .tab-wrapper,.gradio-container .tab-container{overflow-x:auto!important;flex-wrap:nowrap!important;-webkit-overflow-scrolling:touch}
.gradio-container [role="tab"]{white-space:nowrap}
/* تابلت */
@media(max-width:1024px){.gradio-container{padding:10px!important}.brand h1{font-size:1.5rem}}
/* هاتف */
@media(max-width:640px){
 .gradio-container{padding:6px!important}
 .gradio-container .row>*{min-width:100%!important;flex-basis:100%!important}
 .brand img{width:100px}.brand h1{font-size:1.15rem}.brand p{font-size:.75rem}
 .gradio-container table,.gr-dataframe{font-size:12px}
}
'''

def login_action(u,p):
    ok,role=authenticate(u,p)
    if ok:return gr.update(visible=False),gr.update(visible=True),f'✅ تم الدخول بنجاح — الصلاحية: **{role}**',u,role
    return gr.update(visible=True),gr.update(visible=False),'❌ اسم المستخدم أو كلمة المرور غير صحيحة.','',''

def do_search(q,d,y):
    x=search(q,d,y); return f'### 🔎 عدد النتائج: {len(x)}',x

def dashboard():
    total,counts=stats(); return f'## 👥 إجمالي الخريجين: {total}', {str(k):int(v) for k,v in counts.items()}

def detail(reg):
    s=get_student(reg)
    if not s:return '❌ لم يتم العثور على الخريج.'
    return '\n'.join([f'## 🎓 {s["الاسم"]}',f'**رقم التسجيل:** {s["رقم التسجيل"]}  ',f'**الرقم الجامعي:** {s["الرقم الجامعي"]}  ',f'**القسم:** {s["القسم"]}  ',f'**التخصص:** {s["التخصص"]}  ',f'**المعدل:** {s["المعدل التراكمي"]}  ',f'**المرتبة:** {s["تصنيف المرتبة"]}  ',f'**سنة التخرج:** {s["سنة التخرج"]}  ',f'**الإيميل:** {s["الإيميل"]}  ',f'**الهاتف:** {s["الهاتف"]}  ',f'**مشروع التخرج:** {s["مشروع التخرج"]}'])

def clear_edit(): return ('',)*12

with gr.Blocks(title='نظام إدارة خريجي جامعة البطانة',css=CSS,theme=gr.themes.Soft()) as demo:
    gr.HTML(HEADER_HTML)
    with gr.Accordion('🌐 بوابة الخريج العامة — بدون تسجيل دخول', open=True):
        gr.Markdown('يمكن لأي خريج الاستعلام عن بياناته باستخدام رقم التسجيل فقط.')
        pubreg=gr.Textbox(label='رقم التسجيل')
        pubbtn=gr.Button('🔎 استعلام عام',variant='primary')
        pubout=gr.Markdown()
        pubbtn.click(public_search,pubreg,pubout)
    login_box=gr.Group()
    with login_box:
        gr.HTML(LOGIN_LOGO); gr.Markdown('## 🔐 تسجيل الدخول')
        user=gr.Textbox(label='اسم المستخدم',value='admin'); pw=gr.Textbox(label='كلمة المرور',type='password',value='1234'); lb=gr.Button('🔐 دخول',variant='primary'); ls=gr.Markdown()
    main=gr.Group(visible=False)
    with main:
        session_user=gr.State(''); session_role=gr.State('')
        dash=gr.Markdown()
        with gr.Row():
            refresh=gr.Button('🔄 تحديث لوحة التحكم'); logout=gr.Button('🚪 تسجيل الخروج')
        with gr.Tabs():
            with gr.Tab('📊 لوحة التحكم'):
                chart=gr.JSON(label='توزيع الخريجين حسب القسم'); alltable=gr.Dataframe(headers=COLUMNS,interactive=False,wrap=True)
                gr.Markdown('### 📈 إحصائيات سريعة')
                stat=gr.Markdown()
                refresh.click(lambda: (dashboard()[0],dashboard()[1],search()),outputs=[dash,chart,alltable])
            with gr.Tab('🔎 البحث المتقدم'):
                with gr.Row(): q=gr.Textbox(label='بحث شامل'); d=gr.Dropdown(departments(),value='الكل',label='القسم'); y=gr.Dropdown(years(),value='الكل',label='سنة التخرج')
                sb=gr.Button('🔍 بحث',variant='primary'); ss=gr.Markdown(); table=gr.Dataframe(headers=COLUMNS,interactive=False,wrap=True)
                sb.click(do_search,[q,d,y],[ss,table]); q.submit(do_search,[q,d,y],[ss,table])
                gr.Markdown('### 🎓 عرض خريج بالتفصيل'); regdetail=gr.Textbox(label='رقم التسجيل'); detailbtn=gr.Button('عرض التفاصيل'); detailout=gr.Markdown(); detailbtn.click(detail,regdetail,detailout)
            with gr.Tab('➕ إضافة خريج'):
                with gr.Row(): a1=gr.Textbox(label='رقم التسجيل *'); a2=gr.Textbox(label='الرقم الجامعي'); a3=gr.Textbox(label='الاسم *')
                with gr.Row(): a4=gr.Dropdown(departments()[1:],label='القسم'); a5=gr.Textbox(label='التخصص'); a6=gr.Number(label='المعدل'); a7=gr.Textbox(label='تصنيف المرتبة'); a8=gr.Number(label='سنة التخرج',precision=0,value=2026)
                with gr.Row(): a9=gr.Textbox(label='الإيميل'); a10=gr.Textbox(label='الهاتف'); a11=gr.Textbox(label='مشروع التخرج')
                a12=gr.File(label='صورة الخريج',type='filepath'); addb=gr.Button('➕ حفظ',variant='primary'); adds=gr.Markdown()
                addb.click(lambda *v:add_student(v,v[-1] if False else 'admin'),[a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12],[adds,table])
            with gr.Tab('✏️ تعديل / 🗑️ حذف'):
                e1=gr.Textbox(label='رقم التسجيل')
                with gr.Row(): e2=gr.Textbox(label='الرقم الجامعي'); e3=gr.Textbox(label='الاسم'); e4=gr.Dropdown(departments()[1:],label='القسم'); e5=gr.Textbox(label='التخصص')
                with gr.Row(): e6=gr.Number(label='المعدل'); e7=gr.Textbox(label='تصنيف المرتبة'); e8=gr.Number(label='سنة التخرج',precision=0); e9=gr.Textbox(label='الإيميل'); e10=gr.Textbox(label='الهاتف')
                e11=gr.Textbox(label='مشروع التخرج'); e12=gr.File(label='الصورة',type='filepath')
                with gr.Row(): ub=gr.Button('💾 حفظ التعديل',variant='primary'); db=gr.Button('🗑️ حذف',variant='stop')
                es=gr.Markdown(); ub.click(lambda *v:update_student(v),[e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12],[es,table]); db.click(delete_student,e1,[es,table])
            with gr.Tab('📥 Excel والتقارير'):
                gr.Markdown('استيراد ملف Excel يستبدل قاعدة البيانات الحالية بعد التحقق.'); imp=gr.File(label='ملف Excel',type='filepath'); ib=gr.Button('📥 استيراد'); ims=gr.Markdown(); ib.click(import_excel,imp,[ims,alltable]); dl=gr.DownloadButton('⬇️ تصدير Excel'); dl.click(export_excel,outputs=dl)
                backup=gr.Button('💾 إنشاء نسخة احتياطية'); bo=gr.File(label='ملف النسخة الاحتياطية'); backup.click(backup_database,outputs=bo)
                gr.Markdown('### 🖨️ تقرير خريج'); preg=gr.Textbox(label='رقم التسجيل'); pdf=gr.DownloadButton('⬇️ إنشاء/تحميل تقرير PDF');
                def make_pdf(reg):
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import A4
                    s=get_student(reg)
                    if not s:return None
                    path=os.path.join(os.path.dirname(__file__),f'graduate_{reg}.pdf'); c=canvas.Canvas(path,pagesize=A4); y0=780
                    try:
                        from reportlab.pdfbase import pdfmetrics
                        from reportlab.pdfbase.ttfonts import TTFont
                        font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
                        if os.path.exists(font): pdfmetrics.registerFont(TTFont('ArabicFont',font)); c.setFont('ArabicFont',14)
                        else: c.setFont('Helvetica',12)
                    except Exception: c.setFont('Helvetica',12)
                    try: c.drawImage(LOGO_PATH,255,730,width=85,height=85,mask='auto')
                    except Exception: pass
                    y0=700; c.drawCentredString(300,y0,'جامعة البطانة - سجل خريج'); y0-=40; c.setFont('ArabicFont' if 'ArabicFont' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',11)
                    for k,v in s.items():
                        if k=='الصورة': continue
                        c.drawString(60,y0,f'{k}: {v}'); y0-=24
                    c.save(); return path
                pdf.click(make_pdf,preg,pdf)
            with gr.Tab('👥 المستخدمون') as users_tab:
                gr.Markdown('إدارة المستخدمين متاحة للمدير.'); ul=gr.Dataframe(value=users_list(),interactive=False); nu=gr.Textbox(label='اسم المستخدم الجديد'); np=gr.Textbox(label='كلمة المرور'); nr=gr.Dropdown(['مدير','موظف','عرض فقط'],value='موظف',label='الصلاحية'); ub2=gr.Button('➕ إضافة مستخدم'); ud=gr.Textbox(label='اسم المستخدم للحذف'); db2=gr.Button('🗑️ حذف مستخدم'); us=gr.Markdown(); ub2.click(lambda u,p,r:add_user(u,p,r,'admin'),[nu,np,nr],[us,ul]); db2.click(lambda u:delete_user(u,'admin'),ud,[us,ul])
            with gr.Tab('🧾 سجل التدقيق'):
                al=gr.Dataframe(value=audit(),interactive=False); ab=gr.Button('🔄 تحديث السجل'); ab.click(audit,outputs=al)
        gr.Markdown('**بيانات الدخول الافتراضية:** admin / 1234')
    lb.click(login_action,[user,pw],[login_box,main,ls,session_user,session_role])
    logout.click(lambda:(gr.update(visible=True),gr.update(visible=False),''),outputs=[login_box,main,ls])

if __name__=='__main__':
    demo.launch(favicon_path=FAVICON_PATH,allowed_paths=[os.path.join(BASE,'assets')])
