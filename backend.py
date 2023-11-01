import pandas as pd
from fastapi import requests
from flask_mysqldb import MySQL
from NewsAgent import NewsAgent
import re
import openai
from flask_mysqldb import MySQL
from flask import Flask, request, render_template, flash, redirect, url_for, session, jsonify, json


chengdu80_api = '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'
model = 'gpt-4'

option_Dimensions_L1 = ['Technological innovation', 'ESG information']
option_Dimensions_L2 = ['Seceurity and Privacy']


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cd80'
mysql = MySQL(app)
app.secret_key='kdjklfjkd87384hjdhjh'


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    return render_template('register.html')

    # if request.method == 'POST':
    #     # 获取表单数据
    #     email = request.form.get('email')
    #     pwd = request.form.get('pwd')
    #     # 将数据写入数据库
    #     cur = mysql.connection.cursor()
    #     cur.execute(
    #         "INSERT INTO user_info (email, pwd) VALUES ("
    #         "%s, %s)",
    #         (email, pwd))
    #     mysql.connection.commit()
    #     cur.close()
    #     return '注册成功'


@app.route('/industry')
def industry():

    return render_template('industry.html')


@app.route('/dimension')
def dimension():

    return render_template('dimension.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 读取数据
    # df = pd.read_csv('./static/NewsData11.1.csv', encoding='utf-8-sig')
    # # print(df)
    #
    # cur = mysql.connection.cursor()
    # for index, row in df.iterrows():
    #     title = row['title']
    #     content = row['content']
    #     time = row['time']
    #     company_name = row['company']
    #     cur.execute("INSERT INTO news_base (title, time, content, company_name) VALUES (%s, %s, %s, %s)", ( title, time, content, company_name))
    #     mysql.connection.commit()
    # cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT title, time, content FROM news_base")
    data = cur.fetchall()
    result = []
    columns = [column[0] for column in cur.description]  # 获取列名
    for row in data:
        row_dict = {}
        for i in range(len(columns)):
            row_dict[columns[i]] = row[i]
        result.append(row_dict)
    # print(result)
    cur.close()
    # 将json中的数据清空
    with open('./static/newsdata.json', 'w') as f:
        f.truncate(0)
    # 将数据写入 JSON 文件
    with open('./static/newsdata.json', 'w', encoding='utf-8-sig') as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

    return render_template('login.html')


@app.route('/login_btn', methods=['GET', 'POST'])
def login_btn():

    if request.method == 'POST':
        # print (request)
        email = request.form['email']
        pwd = request.form['pwd']
        # print(email)
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM user_info WHERE email = %s and pwd = %s", (email, pwd))
        # print(result)
        if result > 0:
            # return "登录成功"
            # flash('登陆成功！', 'success')
            return redirect(url_for('home'))
        else:
            return render_template('login.html')


# 主页路由
@app.route('/home', methods=['GET', 'POST'])
def home():

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM news_base")
    # mysql.connection.commit()
    # data = cur.fetchall()
    # cur.close()
    # print(data)
    # columns = [column[0] for column in cur.description]  # 获取列名
    #
    # result = []
    # for row in data:
    #     row_dict = {}
    #     for i in range(len(row)):
    #         row_dict[columns[i]] = row[i]
    #     result.append(row_dict)
    # print(result)
    # for i in range(len(result)):
    #     new_id = result[i]['new_id']
    #     title = result[i]['title']
    #     news = result[i]['content']
    #     time = result[i]['time']
    #
    #     single_result = {}
    #     # 获取到了title, news, time的数据
    #     single_result['title'] = title
    #     single_result['news'] = news
    #     single_result['time'] = time
    #     print(single_result)
    #     # prompt
    #     parse_prompt = """You are now a professional financial analyst. Please extract for me a summary of the news through the news text; related entities involved in the news; positive information or opportunities for the market; risks and negative information; explanation of relevant professional terms;and other terms below.
    #
    #                 input:
    #                 [News]:
    #
    #                 output:
    #                 [News Summarization]:
    #                 [Related Entity]:
    #                 [Opportunities and Positive Information]:
    #                 [Risk and Negative Information]:
    #                 [Sentiment]:
    #                 [Explanation of related professional terms]:
    #                 {}
    #
    #                 warning:
    #                 1. Pay attention to the company name, it should be a more important related entity.
    #                 2. When there is no relevant information in the news, please do not infer or associate it. The term return is empty.
    #                 3. [Sentiment] is and can only be positive, negative or neutral.
    #                 """
    #
    #     analyze_prompt = """
    #                 Based on the above information, please analyze and infer the impact of the news from the following aspects and levels, that is, how the news affects the financial market. Please elaborate from the following three perspectives:
    #                 output:
    #                 [policy]:
    #                 [industry]:
    #                 [Public Opinion]:
    #                 {}
    #
    #                 warning:
    #                 1. If a certain dimension is not reflected in the news, please ignore it.
    #                 2. When conducting analysis, avoid using ambiguous expressions. When presenting a viewpoint, establish a mechanism within the analysis.
    #                 """
    #
    #     policy_prompt = """
    #                 Based on the above influential information, please judge whether this news will have a large or lasting impact on the relevant securities markets and commodities.  Please reply yes or no and analyze information with financial value.
    #                 """
    #
    #     industry_prompt = """
    #                 Based on the above influential information, please judge whether this news will have a greater or lasting impact on the securities markets of related industries, commodities in related industries, and investor sentiment. Please reply yes or no and and analyze information with financial value.
    #                 """
    #
    #     Public_prompt = """
    #                 Based on the above influential information, please judge whether this news will have a large or lasting impact on investor sentiment. Please reply yes or no and and analyze information with financial value.
    #                 """
    #
    #     output_prompt = """
    #                 output:
    #                 [Whether it has a greater impact]:
    #                 [analyze]:
    #
    #                 warning:
    #                 1. When conducting analysis, avoid using ambiguous expressions. When presenting a viewpoint, establish a mechanism within the analysis
    #                 """
    #
    #     if option_Dimensions_L1:
    #
    #         add_Dimensions_L1 = ''
    #
    #         for i in option_Dimensions_L1:
    #             add_Dimensions_L1 += '[' + i + ']:' + '\n'
    #
    #         parse_prompt = parse_prompt.format(add_Dimensions_L1)
    #     else:
    #         parse_prompt = parse_prompt.format('')
    #
    #     messages = [{"role": "system", "content": parse_prompt}]
    #
    #     news_agent = NewsAgent(api_key=chengdu80_api, model=model, messages=messages)
    #
    #     parse_news = news_agent.continue_conversation(user_input="Let's begin:[News]:" + news)
    #
    #     if option_Dimensions_L2:
    #
    #         add_Dimensions_L2 = ''
    #
    #         for i in option_Dimensions_L2:
    #             add_Dimensions_L2 += '[' + i + ']:' + '\n'
    #
    #         analyze_prompt = analyze_prompt.format(add_Dimensions_L2)
    #     else:
    #         analyze_prompt = analyze_prompt.format('')
    #
    #     impact = news_agent.continue_conversation(user_input=analyze_prompt)
    #
    #     # 添加query和热点新闻
    #
    #
    #     kg = "Supplementary knowledge:'Policy influence generally has a large impact and high sustainability; industry influence has a large impact but has a short duration; public opinion news has a large impact, has a short duration and is highly volatile'."
    #
    #

    #     cur.execute("SELECT * FROM kg where user_id = 0 or user_id = %s",(user_id))
    #     result = db_operation()

    #
    #     kg_list = []
    #     for i in range(len(result)):
    #       kg_list.append(result[i]['kg_content'])

    #     embedding = OpenAIEmbeddings()
    #     db = Chroma.from_texts(kg_list, embeddings)
    #     similar_docs = db.similarity_search(title, k=1)
    #     kg = "Supplementary knowledge" + similar_docs[0].page_content
    #
    #
    #     kg = "Supplementary knowledge:'Policy influence generally has a large impact and high sustainability; industry influence has a large impact but has a short duration; public opinion news has a large impact, has a short duration and is highly volatile'."
    #     if 'policy' in impact:
    #         user_input = policy_prompt + kg + output_prompt
    #     elif 'industry' in impact:
    #         user_input = industry_prompt + kg + output_prompt
    #     elif 'Public Opinion' in impact:
    #         user_input = Public_prompt + kg + output_prompt
    #     else:
    #         user_input = Public_prompt + kg + output_prompt
    #
    #     analyze = news_agent.continue_conversation(user_input=user_input)
    # def storage_info_csv(news_list, company_name, file_path):
    # with open(file_path, mode='a', newline='', encoding='utf-8-sig') as file:
    #             writer = csv.writer(file)
    #             if file.tell() == 0:
    #                 writer.writerow(['Title', 'URL', 'Description', 'Date Published', 'Company_name', 'category'])
    #             for news in news_list:
    #                 title = clean_html(news['name'])
    #                 url = news['url']
    #                 description = clean_html(news['description'])
    #                 date_published = parse_date(news['datePublished'])
    #                 category = news.get('category',None)
    #                 writer.writerow([title, url, description, date_published, company_name,category])

    #     def get_news_by_query(query,subscription_key,file_path):
    #         params_value = {
    #                 'q': query,
    #                 'mkt': 'en-us',
    #                 'textdecorations': 'true',
    #                 'textformat': 'HTML',
    #                 'count': 100,
    #                 'offset': 0,
    #         }
    #         count = params_value['count']
    #         for i in range(MAX_COUNT // count):
    #             params_value['offset'] = params_value['offset'] + params_value['count'] * i
    #             headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    #             url = 'https://api.bing.microsoft.com/v7.0/news/search'
    #             response = requests.get(url, headers=headers, params=params_value)
    #             response.raise_for_status()

    #             # 解析响应
    #             if response.status_code == 200:
    #                 response_json = response.json()
    #                 news_list = response_json['value']
    #                 return news_list
    #             else:
    #                 print(f'Error: {response.status_code}')
    #                 print(response.text)
    #
    #     def parse_text(text):
    #         sections = re.split(r'(\[\w.*\]:|\n<\w.*>:)', text)
    #         result = {}
    #         current_key = None
    #
    #         for section in sections:
    #             section = section.strip()
    #             if not section:
    #                 continue
    #             if section.startswith('[') or section.startswith('<'):
    #                 current_key = section[1:-2]
    #                 result[current_key] = ''
    #             elif current_key:
    #                 result[current_key] += section + '\n'
    #             else:
    #                 # Handling sections that do not follow the "key: value" format
    #                 if ':' in section:
    #                     key, value = section.split(': ', 0)  # 初始为1
    #                     result[key] = value
    #                 else:
    #                     result[current_key] += section + '\n'
    #         return result
    #
    #     single_result = dict(single_result, **parse_text(parse_news), **parse_text(impact), **parse_text(analyze))
    #     print(single_result)
    #     for key in single_result.keys():
    #         cur = mysql.connection.cursor()
    #         cur.execute("INSERT INTO news_result (new_id, dim_name, dim_content) VALUES ( %s, %s, %s)",
    #                     (new_id, key, single_result[key]))
    #         print(new_id)
    #         mysql.connection.commit()
    #         cur.close()

    return render_template('home.html')


@app.route('/news', methods=['GET', 'POST'])
def news():

    # 将json中的数据清空
    with open('./static/human_pc.json', 'w') as f:
        f.truncate(0)
    # print(87465123)
    # 从数据库读取详细分析
    # 获取点击的事件
    index_value = request.args.get('id')
    # print(index_value)
    cur = mysql.connection.cursor()
    print(index_value)
    cur.execute("SELECT * FROM news_result where new_id = %s", (index_value),)
    mysql.connection.commit()
    data = cur.fetchall()
    cur.close()
    # print(data)

    dimension_dict = {}
    result = list(data)
    for i in range(len(result)):
        for j in range(len(result[i])):
            if j == (len(result[i]) - 1):
                dimension_dict[result[i][j - 1]] = result[i][j]
    # print(dimension_dict)

    # 将json中的数据清空
    with open('./static/news_result.json', 'w') as f:
        f.truncate(0)
    # 将数据写入 JSON 文件
    with open('./static/news_result.json', 'w', encoding='utf-8') as f:
        json.dump(dimension_dict, f, indent=2, sort_keys=True, ensure_ascii=False)

    return render_template('news.html')


# @app.route('/merge_news', methods=['GET', 'POST'])
# def merge_news():
#
#     # 将json中的数据清空
#     with open('./static/human_pc.json', 'w') as f:
#         f.truncate(0)
#     # print(87465123)
#     # 从数据库读取详细分析
#     # 获取点击的事件
#     index_value = request.args.get('id')
#     # print(index_value)
#     cur = mysql.connection.cursor()
#     # cur.execute("SELECT * FROM news_result where new_id = %s", (index_value),)
#     mysql.connection.commit()
#     data = cur.fetchall()
#     cur.close()
#     # print(data)
#
#     dimension_dict = {}
#     result = list(data)
#     for i in range(len(result)):
#         for j in range(len(result[i])):
#             if j == (len(result[i]) - 1):
#                 dimension_dict[result[i][j - 1]] = result[i][j]
#     # print(dimension_dict)
#
#     # 将json中的数据清空
#     with open('./static/news_result.json', 'w') as f:
#         f.truncate(0)
#     # 将数据写入 JSON 文件
#     with open('./static/news_result.json', 'w', encoding='utf-8') as f:
#         json.dump(dimension_dict, f, indent=2, sort_keys=True, ensure_ascii=False)
#
#     return render_template('home.html')


@app.route('/human_pc', methods=['GET', 'POST'])
def human_pc():

    if request.method == 'POST':
        user_interact = request.form['text']
    AI_analyze = """
        The news of a potential import ban on one of Apple's key products could have a significant and lasting impact on the relevant securities markets. Apple is a major player in the tech industry and any disruption to its operations could have ripple effects across the market. The potential policy implications of the court ruling could also lead to long-term changes in the industry, particularly in terms of intellectual property rights enforcement. This could affect not only Apple but also other tech companies, potentially leading to increased volatility in the tech securities market. \n\nIn terms of commodities, if the banned product is a major revenue driver for Apple, the ban could lead to a decrease in demand for the raw materials used in its production. This could impact the commodities market, particularly if these materials are specialized and not easily repurposed for other products. \n\nHowever, the duration and extent of these impacts would depend on several factors, including the specific product involved, the length of the ban, and the response from Apple and other industry players.
        """

    interraction_prompt = """
        I will now give you a piece of text analyzed by AI and interactive feedback from users. You need to find the differences between the two parties and summarize them. For the financial market, differences are the most valuable content. Finally, I need you to turn the summarized differences into a logical and useful mind map for guidance next analysis:

        input:
        [AI analyze]:
        [User_interact]:

        output:
        [Disagreement]:
        [Knowledge Graph]:

        1.If there is no disagreement, output the truth and return nothing.
        2.entity nodes with relationship paths should be tried to be associated to expand into a text-based mind map.
        3.After outputting the complete mindmap, interrupt the output and do not perform inference analysis. no further explanation.
        """

    def parse_text(text):
        sections = re.split(r'(\[\w.*\]:|\n<\w.*>:)', text)
        result = {}
        current_key = None

        for section in sections:
            section = section.strip()
            if not section:
                continue
            if section.startswith('[') or section.startswith('<'):
                current_key = section[1:-2]
                result[current_key] = ''
            elif current_key:
                result[current_key] += section + '\n'
            else:
                # Handling sections that do not follow the "key: value" format
                if ':' in section:
                    key, value = section.split(': ', 0)  # 初始为1
                    result[key] = value
                else:
                    result[current_key] += section + '\n'
        return result

    KG_prompt = """
        I will give you an analysis. Please convert this analysis into a refined logical route, in which entities are represented by points, relationships and reasoning are represented by edges, and finally a mindmap is generated.

        input:
        [analyze]:

        ouput:
        [mindmap]:

        warning:
        1.If the given analysis is empty or has no obvious knowledge,, output the truth and return nothing.
        2.After outputting the complete mindmap, interrupt the output and do not perform inference analysis. no further explanation.
        3.No need for any text supplements or prompts.
        """

    Correlation = "The two pieces of news are correlated as they both involve Apple Inc., one of the world's leading technology companies. The first article discusses a legal battle between Apple and entrepreneur Joe Kiani, which could potentially lead to a ban on one of Apple's key products in the United States. The second article discusses the launch of Apple's iPhone 15 Pro and its failure to meet expectations, with Google's Pixel 8 Pro seizing the advantage in the smartphone market"
    tracking = "The first event, dated 2023-10-27, marks a significant legal setback for Apple, as it faces the potential ban of one of its key products in the U.S. due to the court battle with Joe Kiani. This could have a significant impact on Apple's market share and revenue in the U.S., which is one of its largest markets.\n\nThe second event, dated 2023-10-28, further compounds Apple's challenges. The launch of the iPhone 15 Pro, which was expected to redefine the smartphone market, failed to deliver on its promise. Instead, Google's Pixel 8 Pro has seized the advantage, indicating a shift in the competitive dynamics of the smartphone market. This could further erode Apple's market share and profitability.\n\nIn conclusion, these two events, occurring in close succession, could have a significant negative impact on Apple's business performance. The potential ban of a key product in the U.S. and the failure of the iPhone 15 Pro to meet expectations could lead to a decline in Apple's market share and profitability. This could also affect investor confidence in the company, leading to a potential decline in its stock price."
    Analyze = "The news of a potential import ban on one of Apple's key products could have a significant and lasting impact on the relevant securities markets. Apple is a major player in the tech industry and any disruption to its operations could have ripple effects across the market. The potential policy implications of the court ruling could also lead to long-term changes in the industry, particularly in terms of intellectual property rights enforcement. This could affect not only Apple but also other tech companies, potentially leading to increased volatility in the tech securities market. \n\nIn terms of commodities, if the banned product is a major revenue driver for Apple, the ban could lead to a decrease in demand for the raw materials used in its production. This could impact the commodities market, particularly if these materials are specialized and not easily repurposed for other products. \n\nHowever, the duration and extent of these impacts would depend on several factors, including the specific product involved, the length of the ban, and the response from Apple and other industry players."

    kg = """
        The Echo Chamber Effect:
        The tendency of digital algorithms to show users news that aligns with their existing beliefs can create echo chambers and contribute to polarization.
        """

    # 获取Dis_KG_dict
    messages = [{"role": "system", "content": interraction_prompt}]

    news_agent = NewsAgent(api_key=chengdu80_api, model=model, messages=messages)

    Dis_KG = news_agent.continue_conversation(
        user_input="Let's begin:[AI analyze]:" + AI_analyze + '/n' + '[User_interact]:' + user_interact)

    Dis_KG_dict = parse_text(Dis_KG)

    # 获取disaggrement, knowledge graph
    disaggrement = Dis_KG_dict['Disagreement']
    Knowledge_Graph = Dis_KG_dict['Knowledge Graph']

    # 获取mindmap
    messages = [{"role": "system", "content": KG_prompt}]

    news_agent = NewsAgent(api_key=chengdu80_api, model=model, messages=messages)

    KG = news_agent.continue_conversation(user_input="Let's begin:[analyze]:" + kg)

    KG_dict = parse_text(KG)

    # 获取mindmap
    mindmap = KG_dict['mindmap']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO kg (user_id, kg_content, mindmap) VALUES ( %s, %s, %s)",
                (1, Knowledge_Graph, mindmap))
    mysql.connection.commit()
    cur.close()

    print(disaggrement)


    # 将数据写入 JSON 文件
    with open('./static/human_pc.json', 'w', encoding='utf-8') as f:
        json.dump(disaggrement, f, indent=2, sort_keys=True, ensure_ascii=False)

    return render_template('news.html')


@app.route('/hot', methods=['GET', 'POST'])
def hot():

    cur = mysql.connection.cursor()
    cur.execute("SELECT new_id FROM news_result where dim_name = 'Whether it has a greater impact' and dim_content LIKE '%Yes%' ")
    mysql.connection.commit()
    data = cur.fetchall()
    cur.close()
    print(data)

    data = list(data)
    res = []
    for i in range(len(data)):
        res.append(data[i][0])
    res

    result = []
    for i in res:
        cur = mysql.connection.cursor()
        cur.execute("SELECT title, time, content FROM news_base where new_id = %s", (i, ))
        mysql.connection.commit()
        data = cur.fetchall()
        columns = [column[0] for column in cur.description]  # 获取列名
        for row in data:
            row_dict = {}
            for i in range(len(columns)):
                row_dict[columns[i]] = row[i]
            result.append(row_dict)
        # print(result)
        cur.close()
    # 将json中的数据清空
    with open('./static/news_hot.json', 'w') as f:
        f.truncate(0)
    # 将数据写入 JSON 文件
    with open('./static/news_hot.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

    return render_template('home_hot.html')


@app.route('/relate', methods=['GET', 'POST'])
def relate():
    cur = mysql.connection.cursor()

    # 得到多条新闻的id
    cur.execute("SELECT * FROM news_base WHERE new_id = 1 OR new_id = 2")

    mysql.connection.commit()
    data = cur.fetchall()
    cur.close()

    columns = [column[0] for column in cur.description]  # 获取列名

    result = []
    for row in data:
        row_dict = {}
        for i in range(len(columns)):
            row_dict[columns[i]] = row[i]
        result.append(row_dict)

    # 将json中的数据清空
    with open('./static/news_2.json', 'w') as f:
        f.truncate(0)
    # 将数据写入 JSON 文件
    with open('./static/news_2.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, sort_keys=True, ensure_ascii=False)

    # 设置多条新闻的列表
    news = []
    times = []
    for i in range(len(result)):
        news.append(result[i]['content'])
        times.append(result[i]['time'])

    # 检查时间和新闻列表的长度是否相等
    if len(news) != len(times):
        print("新闻和时间的数量不一致！")
    else:
        # 使用zip函数将时间和新闻配对，并使用循环遍历它们
        co_news = ''
        for t, n in zip(times, news):
            # 使用字符串格式化拼接时间和新闻，并添加换行符
            co_news += f"{t}: {n}\n"

    correlation_prompt = """
           Now, as a professional financial analyst, please comprehensively analyze multiple pieces of news, determine whether there is correlation between articles, and provide explanations;If there is a correlation, track the impact of news events chronologically.

           input:
           [time & news]:

           output:
           [Correlation]: 
           [tracking]:


           warning：
           1. When conducting analysis, avoid using ambiguous expressions. When presenting a viewpoint, establish a mechanism within the analysis.
           2. For tracking analysis, please conduct in-depth analysis and provide a clear logical chain.
        """

    def parse_text(text):
        sections = re.split(r'(\[\w.*\]:|\n<\w.*>:)', text)
        result = {}
        current_key = None

        for section in sections:
            section = section.strip()
            if not section:
                continue
            if section.startswith('[') or section.startswith('<'):
                current_key = section[1:-2]
                result[current_key] = ''
            elif current_key:
                result[current_key] += section + '\n'
            else:
                # Handling sections that do not follow the "key: value" format
                if ':' in section:
                    key, value = section.split(': ', 0)  # 初始为1
                    result[key] = value
                else:
                    result[current_key] += section + '\n'
        return result

    messages = [{"role": "system", "content": correlation_prompt}]
    news_agent = NewsAgent(api_key=chengdu80_api, model=model, messages=messages)
    parse_news = news_agent.continue_conversation(user_input="Let's begin:[time & news]:" + co_news)
    co_dict = parse_text(parse_news)
    # return result

    # 将json中的数据清空
    with open('./static/correlation.json', 'w') as f:
        f.truncate(0)
    # 将数据写入 JSON 文件
    with open('./static/correlation.json', 'w', encoding='utf-8') as f:
        json.dump(co_dict, f, indent=2, sort_keys=True, ensure_ascii=False)
    return render_template('correlate.html')


if __name__ == '__main__':
    app.run(debug=True)
