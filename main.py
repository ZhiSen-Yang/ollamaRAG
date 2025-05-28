import datetime
import json
import time

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from langchain.chains.chat_vector_db.prompts import prompt_template

from init import llm, db, config
from task import start_file_watcher

app = Flask(__name__)
CORS(app, supports_credentials=True)
def json_response(data=None, code=200, msg="success"):
    payload = {
        "code": code,
        "msg": msg,
        "data": data
    }
    return Response(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )
@app.route("/ocrpdf", methods=['get'])
def test():
    text=request.args.get('a')
    def generate():
        retriever = db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(text)
        context = "\n".join([doc.page_content for doc in docs])
        prompt = prompt_template.format(context=context, question=text)

        for chunk in llm.stream(prompt):
           # print("📌 回答：", chunk, flush=True)
            yield chunk
            time.sleep(0.01)
    return Response(generate(), content_type='text/event-stream; charset=utf-8')


if __name__ == '__main__':
    try:
        start_file_watcher()
        print("✅ 文件监控线程已启动，主程序继续运行")
        app.config['JSON_AS_ASCII'] = False
        print("项目名：", config["app"]["file"]["path"])
        #服务器名称不能有中文
        app.run(host='0.0.0.0',port=8059,threaded=True)

    except:
        errorLog = open("Log.log", "a")
        import traceback
        now=datetime.datetime.now()
        st=now.strftime("%Y-%m-%d %H:%M:%S",now)
        errorLog.write(u"时间:{0}\n{1}\n".format(st,traceback.format_exc()))
        # 关闭打开的文件
        errorLog.close()
