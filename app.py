# app.py

import inspect
# Monkey patch для Python 3.11: додаємо inspect.getargspec, якщо його немає
if not hasattr(inspect, 'getargspec'):
    def getargspec(func):
        fullargspec = inspect.getfullargspec(func)
        return fullargspec.args, fullargspec.varargs, fullargspec.varkw, fullargspec.defaults
    inspect.getargspec = getargspec

from flask import Flask, render_template, request, send_file, jsonify
from docxtpl import DocxTemplate
import datetime
from io import BytesIO
import pymorphy2

app = Flask(__name__)
morph = pymorphy2.MorphAnalyzer(lang='uk')

def inflect_phrase_multiword(phrase, tags):
    # Розбиваємо фразу на окремі слова
    words = phrase.split()
    inflected_words = []
    for word in words:
        p = morph.parse(word)[0]
        inflected = p.inflect(tags)
        if inflected:
            inflected_words.append(inflected.word)
        else:
            inflected_words.append(word)
    return " ".join(inflected_words)

def format_date(date_str):
    """
    Перетворює дату з формату 'yyyy-mm-dd' у 'dd.mm.yyyy'
    """
    try:
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d.%m.%Y')
    except Exception:
        return date_str

def get_name_inflections(surname, name, patronymic):
    """
    Генерує два варіанти з ініціалами:
      - Родового відмінку: наприклад, "Андрусова О.В."
      - Орудного відмінку: наприклад, "Андрусівою О.В."
    """
    # Формуємо ініціали
    initials = ""
    if name:
        initials += name[0] + "."
    if patronymic:
        initials += patronymic[0] + "."

    parsed_list = morph.parse(surname)
    if not parsed_list:
        return (f"{surname} {initials}".strip(), f"{surname} {initials}".strip())

    p = parsed_list[0]
    # Теги для родового та орудного відмінків
    tags_for_genitive = {'gent'}
    tags_for_instrumental = {'ablt'}

    p_gen = p.inflect(tags_for_genitive)
    if p_gen:
        surname_genitive = p_gen.word.capitalize()
    else:
        surname_genitive = surname.capitalize()
    genitive_variant = f"{surname_genitive} {initials}".strip()

    p_ablt = p.inflect(tags_for_instrumental)
    if p_ablt:
        surname_instrumental = p_ablt.word.capitalize()
    else:
        surname_instrumental = surname.capitalize()
    instrumental_variant = f"{surname_instrumental} {initials}".strip()

    return genitive_variant, instrumental_variant

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inflect', methods=['GET'])
def inflect():
    """
    Ендпоінт для отримання:
      - Родового відмінку (з ініціалами)
      - Орудного відмінку (з ініціалами)
    Приймає параметри: surname, name, patronymic.
    """
    surname = request.args.get('surname', '').strip()
    name = request.args.get('name', '').strip()
    patronymic = request.args.get('patronymic', '').strip()

    if not surname or not name or not patronymic:
        return jsonify({'error': 'Усі поля (Прізвище, Ім’я, По-батькові) мають бути заповнені.'}), 400

    genitive_variant, instrumental_variant = get_name_inflections(surname, name, patronymic)
    return jsonify({
        'genitive_variant': genitive_variant,
        'instrumental_variant': instrumental_variant
    })

@app.route('/report', methods=['POST'])
def report():
    """
    Генерує DOCX-рапорт за даними форми.
    Дані підставляються у шаблон report_template_wid.docx.
    """
    # Дані для інформації про матеріали
    military_department_sender = request.form.get('military_department_sender')
    SZC_date = format_date(request.form.get('SZC_date'))
    SZC_time = request.form.get('SZC_time')
    crime_type_value = request.form.get('crime_type_select')
    genitive = inflect_phrase_multiword(crime_type_value, {'gent'})
    instrumental = inflect_phrase_multiword(crime_type_value, {'ablt'})
    military_department_receiver = request.form.get('military_department_receiver')
    issued_document_number = request.form.get('issued_document_number')
    issued_date = format_date(request.form.get('issued_date'))
    dbr_incoming_number = request.form.get('dbr_incoming_number')
    dbr_issued_date = format_date(request.form.get('dbr_issued_date'))
    meta = request.form.get('meta')

    # Дані про ПІП
    surname = request.form.get('surname')
    name = request.form.get('name')
    patronymic = request.form.get('patronymic')
    full_name_variant = f"{surname} {name} {patronymic}".strip()

    # Отримані інфліковані варіанти (редаговані користувачем)
    genitive_variant = request.form.get('genitive_output')
    instrumental_variant = request.form.get('instrumental_output')

    # Дані про адресу
    address = request.form.get('address')

    # Дані для випадаючих списків
    crime_type_select = request.form.get('crime_type_select')
    if crime_type_select == "custom":
        crime_type = request.form.get('crime_type_custom')
    else:
        crime_type = crime_type_select

    crime_place_select = request.form.get('crime_place_select')
    if crime_place_select == "custom":
        crime_place = request.form.get('crime_place_custom')
    else:
        crime_place = crime_place_select

    context = {
        'military_department_sender': military_department_sender,
        'SZC_date': SZC_date,
        'military_department_receiver': military_department_receiver,
        'issued_document_number': issued_document_number,
        'issued_date': issued_date,
        'dbr_incoming_number': dbr_incoming_number,
        'dbr_issued_date': dbr_issued_date,
        'SZC_time': SZC_time,
        'full_name_variant': full_name_variant,
        'genitive_variant': genitive_variant,
        'instrumental_variant': instrumental_variant,
        'service_type': request.form.get('service_type'),
        'position': request.form.get('position'),
        'birth_date': format_date(request.form.get('birth_date')),
        'crime_type': crime_type,
        'crime_place': crime_place,
        'address': address,
        'crime_type_nominative': crime_type_value,
        'crime_type_genitive': genitive,
        'crime_type_instrumental': instrumental,
        'meta': meta
    }
    
    doc = DocxTemplate("report_template.docx")
    doc.render(context)
    
    f = BytesIO()
    doc.save(f)
    f.seek(0)
     # Формуємо ім'я файлу: Прізвище та ініціали + військова частина відправника
    # Наприклад, "Андрусів О.В. A2900.docx"
    file_name = f"{surname} {name[0]}.{patronymic[0]}. {military_department_sender}.docx"
    return send_file(
        f,
        as_attachment=True,
        download_name=file_name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

if __name__ == '__main__':
    app.run(debug=True)