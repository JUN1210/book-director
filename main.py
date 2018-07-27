import direction
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('input.html')


@app.route("/output", methods=["POST"])
def output():
    search_keyword1 = request.form["keyword1"]
    search_keyword2 = request.form["keyword2"]
    search_keyword3 = request.form["keyword3"]
#    output_df = direction.main(search_keyword)
    return redirect(url_for("redirect_test", keyword1 = search_keyword1,
                                             keyword2 = search_keyword2,
                                             keyword3 = search_keyword3))
#                                             output_df = output_df))


@app.route("/redirect_test", methods=["GET"])
def redirect_test():
    keyword1 = request.args.get("keyword1", "")
    keyword2 = request.args.get("keyword2", "")
    keyword3 = request.args.get("keyword3", "")
    output_df = direction.main(keyword1, keyword2, keyword3)
#    output_table = direction.main(search_keyword)
    output_df.to_csv("datatable.csv")
    return render_template("output.html", keyword1 = keyword1,
                                          keyword2 = keyword2,
                                          keyword3 = keyword3,
                                          output_df = output_df)


@app.route("/printout", methods=["POST"])
def printout():
    orders = request.form.getlist("order")
#   output_df = output_df
    ordersJAN = ",".join(orders)
    return redirect(url_for("redirect_print", orders = ordersJAN))
#                                                output_df = output_df))


@app.route("/redirect_print", methods=["GET"])
def redirect_print():
    orders = request.args.get("orders", "")
    output_df = pd.read_csv("datatable.csv", sep=",")
    return render_template("printout.html", orders = orders,
                                            output_df = output_df)
