import datetime
import json
import time

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from langchain.agents import AgentType, initialize_agent
from langchain.chains.chat_vector_db.prompts import prompt_template
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool

from fileUtils import get_save_dir
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
def ocrpdf():
    text=request.args.get('a')
    search_tool = DuckDuckGoSearchRun(k=10)
    search_result = search_tool.run(text)
    print("联网搜索结果", {search_result})
    def generate():
        retriever = db.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(text)
        context = "\n".join([doc.page_content for doc in docs])
        print("RAG 检索结果：", context)
        parts = []
        if context.strip():
            parts.append(f"【本地知识库结果】：\n{context}")
        if search_result.strip():
            parts.append(f"【联网搜索结果】：\n{search_result}")
        parts.append(f"用户问题：{text}\n请先详细说明你的思考过程，然后给出答案：")
        prompt ="\n\n".join(parts)

        for chunk in llm.stream(prompt):
           # print("📌 回答：", chunk, flush=True)
            yield chunk
            time.sleep(0.01)
    return Response(generate(), content_type='text/event-stream; charset=utf-8')
@app.route("/ocrWebPdf", methods=['get'])
def ocrWebPdf():
    text=request.args.get('a')
    search_tool = DuckDuckGoSearchRun()
    search_result = search_tool.run(text)
    print("联网搜索结果",{search_result})
    # 将搜索结果交给模型生成回答
    prompt = f"""根据以下搜索结果回答用户的问题：
    问题：{text}
    联网搜索结果：{search_result}
    请用简洁准确的语言作答："""

    answer = llm.invoke(prompt)
    print(answer)
    return Response(answer, content_type='text/event-stream; charset=utf-8')

# @app.route("/fileUpload", methods=['post'])
# def fileUpload():
#     file=request.files.get('file')
#     filename= get_save_dir(0)+file.filename
#     file.save(filename)
#     return jsonify({"success": 0})
@app.route("/fileUpload", methods=['POST'])
def file_upload():
    files = request.files.getlist('file')  # 获取多个文件
    if not files:
        return jsonify({"success": 0, "msg": "没有接收到文件"})

    saved_files = []
    for file in files:
        if file.filename == '':
            continue
        save_path = get_save_dir(0)+file.filename
        file.save(save_path)
        saved_files.append(file.filename)

    return jsonify({
        "success": 1,
        "msg": f"{len(saved_files)} 个文件上传成功",
        "files": saved_files
    })

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
