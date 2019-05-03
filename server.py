import http.server
import termcolor
import socketserver
import http.client
import json
from Seq import Seq

PORT = 8000


class TestHandler(http.server.BaseHTTPRequestHandler):

    # The following function belongs to the advanced level and it allows to find the variables for each resource that
    # can be requested from the web page by creating a dictionary will all of them.

    def create_dict(self, path):
        my_dict = dict()
        if '?' in path:
            divide = path.split("?")[1]
            divide = divide.split(" ")[0]
            divide_list = divide.split("&")
            for element in divide_list:
                cut = element.split("=")
                key_dict = cut[0]
                value_dict = cut[1]
                my_dict[key_dict] = value_dict
        return my_dict

    # The following function is the main function of the program.

    def do_GET(self):
        termcolor.cprint(self.requestline, 'yellow')
        json_send = False
        status = 200

        # In case the main resource is requested, sends the main web page (index.html).

        if self.path == "/" or self.path == "/index.html":
            name_file = "index.html"
            with open(name_file, "r") as file:
                contents = file.read()

        # For /listSpecies resource.

        elif "/listSpecies" in self.path:
            # Open connection with Ensemble
            names = self.create_dict(self.path)
            conn = http.client.HTTPConnection("rest.ensembl.org")
            conn.request("GET", "/info/species?content-type=application/json")
            r1 = conn.getresponse()
            print()
            print("Response received: ", end='')
            print(r1.status, r1.reason)
            text_json = r1.read().decode("utf-8")
            answer = json.loads(text_json)
            all_species = answer["species"]
            conn.close()

            try:
                limit = int(names["limit"])  # Check if the argument limit has an actual value.
                # If it does, it will be stored.
            except:
                limit = int(len(all_species))  # Sort all the species when limit does not have a value.

            # All this conditional clauses along the practice help to identify whether the user is requesting the info
            # in json format. The variable json_send will determine the way we send this info, which is better explained
            # in the last lines of the practice, where we can find the conditional clauses in which this variable is
            # referenced.

            if "json" in names and names["json"] == "1":
                json_send = True
                my_list = []
                for specie in all_species[0:limit]:
                    my_list.append(specie["display_name"] + "   " + "-" + "   " + specie["name"])
                contents = json.dumps(my_list)
            else:
                json_send = False
                contents = """<html><title>All species - limit</title>
                <body style="background-color: springgreen;"><h1>Limited list requested</h1>
                <ol>"""

                # Now, the limit will always have a value, which will make this loop work.
                for specie in all_species[0:limit]:
                    contents = contents+"<li>"+specie["display_name"] + "   " + "-" + "   " + specie["name"] + "</li>"
                contents = contents+"""</ol><a href = "http://127.0.0.1:8000/">Click here to return to the main page</a>
                </body>
                </html>"""

            # Error page in case the number requested is bigger than the total number of species
            if limit > len(all_species):
                status = 400
                contents = """<html>
                <body style = "background-color: red;">
                <title>Error page</title>
                <h1>Error !</h1>
                <p>The number requested is bigger than the actual list of species.</p>
                <a href="http://127.0.0.1:8000/">Return to the main page</a>
                </body>
                </html>"""

        # For /karyotype resource.

        elif "/karyotype" in self.path:
            names = self.create_dict(self.path)
            specie = names["specie"]
            try:
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "/info/assembly/"+specie+"?content-type=application/json")
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                text_json = r1.read().decode("utf-8")
                answer = json.loads(text_json)
                print(answer)
                gene_list = answer["karyotype"]
                conn.close()

                if "json" in names and names["json"] == "1":
                    json_send = True
                    contents = json.dumps(gene_list)
                else:
                    json_send = False
                    contents = """<html><title>Karyotype</title>
                    <body style= "background-color: springgreen;"><h1>Karyotype requested</h1>
                    <ul>"""
                    for chromosome in gene_list:
                        contents = contents + "<li>" + chromosome + "</li>"
                    contents = contents + """</ul><a href = "http://127.0.0.1:8000/">Click here to return to the main page</a></body>
                    </html>"""
            except TypeError:
                status = 400
                # Error page for when the user does not introduce a species or it does not exist.
                with open("error2.html", "r") as file:
                    contents = file.read()
            except KeyError:
                status = 400
                with open("error2.html", "r") as file:
                    contents = file.read()

        # For /chromosomeLength resource.

        elif "/chromosomeLength" in self.path:
            names = self.create_dict(self.path)
            try:
                chromosome = names["chromo"]
                specie = names["specie"]  # Obtained the name of the chromosome
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "/info/assembly/"+specie+"?content-type=application/json")
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                text_json = r1.read().decode("utf-8")
                answer = json.loads(text_json)
                info = answer["top_level_region"]
                conn.close()
                for number in info:  # Check the name is correct and print the information
                    if number["name"] == chromosome:
                        length = str(number["length"])

                if "json" in names and names["json"] == "1":
                    json_send = True
                    contents = json.dumps(length)
                else:
                    json_send = False
                    contents = """<html><title>Length</title>
                    <body style = "background-color: springgreen;"><h1>Length</h1>
                    <p>The length of the requested chromosome is:</p><h2>""" + length + """</h2>
                    <a href = "http://127.0.0.1:8000/">Click here to return to the main page</a>
                    </body></html>"""

            except KeyError:
                status = 400
                # Error page in case the chromosome does not exist or the user did not write in the text box
                with open("error3.html", "r") as file:
                    contents = file.read()

            except UnboundLocalError:
                status = 400
                # Error page related to the json format request of the user.
                with open("error3.html", "r") as file:
                    contents = file.read()

        # For /geneSeq resource.

        elif"/geneSeq" in self.path:
            try:
                names = self.create_dict(self.path)
                gene = names["gene"]
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "homology/symbol/human/"+gene+"?content-type=application/json")
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                text_json = r1.read().decode("utf-8")
                answer = json.loads(text_json)
                id_gene = answer["data"][0]["id"]  # Obtain the id of the chromosome
                conn.close()
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "/sequence/id/"+id_gene+"?content-type=application/json")
                r2 = conn.getresponse()
                text_json2 = r2.read().decode("utf-8")
                answer2 = json.loads(text_json2)
                sequence = answer2["seq"]

                if "json" in names and names["json"] == "1":
                    json_send = True
                    contents = json.dumps(sequence)
                else:
                    contents = """<html><title>"""+gene+""" sequence</title>
                    <body style = "background-color: springgreen;"><h1>""" + gene + """</h1>
                    <p>The sequence of the requested gene is:</p><h2>""" + sequence + """</h2>
                    <a href = "http://127.0.0.1:8000/">Click here to return to the main page</a>
                    </body></html>"""

            except KeyError:
                status = 400
                # Error page in case the user does not introduce a value or it does not exist.
                with open("error4.html", "r") as file:
                    contents = file.read()

        # For /geneInfo resource.

        elif "/geneInfo" in self.path:
            try:
                names = self.create_dict(self.path)
                gene = names["gene"]
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "homology/symbol/human/" + gene + "?content-type=application/json")
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                text_json = r1.read().decode("utf-8")
                answer = json.loads(text_json)
                id_gene = answer["data"][0]["id"]  # Obtain the id of the chromosome
                conn.close()
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "/overlap/id/"+id_gene+"?feature=gene;content-type=application/json")
                r2 = conn.getresponse()
                text_json2 = r2.read().decode("utf-8")
                answer2 = json.loads(text_json2)
                start_point = answer2[0]["start"]  # Obtained starting point
                end_point = answer2[0]["end"]  # Obtained ending point
                length = end_point - start_point  # Obtained length by subtracting then starting to the ending point
                chromo = answer2[0]["assembly_name"]  # Obtained the name of the chromosome

                if "json" in names and names["json"] == "1":
                    json_send = True
                    info = ("Starting point: " + str(start_point), "Ending point: " + str(end_point), "Length: " +
                                          str(length), "Chromosme: " + chromo)
                    contents = json.dumps(info)
                else:
                    contents = """<html><title>""" + gene + """ info</title>
                    <body style = "background-color: springgreen;"><h1>""" + str(gene) + """</h1>
                    <p>The starting point of the requested gene is:</p><h2>""" + str(start_point) + """</h2>
                    <p>The ending point of the requested gene is:</p><h2>""" + str(end_point) + """</h2>
                    <p>The length of the gene requested is:</p><h2>""" + str(length) + """</h2>
                    <p>The id of the gene requested is:</p><h2>""" + str(id_gene) + """</h2>
                    <p>The chromosome in which the gene requested is located is:</p><h2>""" + str(chromo) + """</h2>
                    <a href = "http://127.0.0.1:8000/">Click here to return to the main page</a>
                    </body></html>"""
            except KeyError:
                status = 400
                # Error page in case the user does not introduce a value or it does not exist.
                with open("error4.html", "r") as file:
                    contents = file.read()

        # For /geneCal resource.

        elif "/geneCalc" in self.path:
            try:
                names = self.create_dict(self.path)
                gene = names["gene"]
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "homology/symbol/human/" + gene + "?content-type=application/json")
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                text_json = r1.read().decode("utf-8")
                answer = json.loads(text_json)
                id_gene = answer["data"][0]["id"]  # Obtain the id of the chromosome
                conn.close()
                conn = http.client.HTTPConnection("rest.ensembl.org")
                conn.request("GET", "/sequence/id/" + id_gene + "?content-type=application/json")
                r2 = conn.getresponse()
                text_json2 = r2.read().decode("utf-8")
                answer2 = json.loads(text_json2)
                sequence = answer2["seq"]

                # Calculate different parameters through the Seq class we made.
                sequence_ob = Seq(sequence)
                length_ob = len(sequence)
                a_perc = sequence_ob.perc("A")
                c_perc = sequence_ob.perc("C")
                g_perc = sequence_ob.perc("G")
                t_perc = sequence_ob.perc("T")

                if "json" in names and names["json"] == "1":
                    json_send = True
                    info = ("Total length: " + str(length_ob), "Percentage A: " + str(a_perc) + "%",
                            "Percentage C: "+ str(c_perc) + "%", "Percentage G: " + str(g_perc) + "%",
                            "Percentage T:  " + str(t_perc) + "%")
                    contents = json.dumps(info)
                else:
                    contents = """<html><title>"""+gene+""" calculations</title>
                    <body style = "background-color: springgreen;"><h1>""" + gene + """</h1>
                    <p>The sequence of the length gene is:</p><h2>""" + str(length_ob) + """</h2>
                    <p>The percentage for each base is:</p>
                    <li>A: """ + str(a_perc) + """%</li><li>C: """ + str(c_perc) + """%</li>
                    <li>G: """ + str(g_perc) + """%</li><li>T: """ + str(t_perc) + """%<br>
                    <a href = "http://127.0.0.1:8000/">Click here to return to the main page</a></body></html>"""
            except KeyError:
                status = 400
                # Error page in case the user does not introduce a value or it does not exist.
                with open("error4.html", "r") as file:
                    contents = file.read()

        # For /geneList resource.

        elif "/geneList" in self.path:
            try:
                names = self.create_dict(self.path)
                chromo = names["chromo"]
                start_point = names["start"]
                end_point = names["end"]
                conn = http.client.HTTPConnection("rest.ensembl.org")
                # This way we only browse genes and not other type of molecule stored in a chromosome (exons, etc)
                conn.request("GET", "/overlap/region/human/" + str(chromo) + ":" + str(start_point) + "-" + str(end_point) +
                             "?content-type=application/json;feature=gene")
                r1 = conn.getresponse()
                print()
                print("Response received: ", end='')
                print(r1.status, r1.reason)
                text_json = r1.read().decode("utf-8")
                answer = json.loads(text_json)

                if "json" in names and names["json"] == "1":
                    json_send = True
                    my_list = []
                    for item in answer:
                        if item["feature_type"] == "gene":
                            my_list.append(item["external_name"] + " " + "Start: " + str(item["start"]) + " " +
                                           "End: " + str(item["end"]))
                    contents = json.dumps(my_list)
                else:
                    contents = """<html><body style="background-color: springgreen;"><title>Genes</title><ul>
                    <h1>Genes from position """ + start_point + """ to """ + end_point + """</h1>"""
                    for item in answer:
                         contents = contents + "<li>" + item["external_name"] + " " + "<h3>Start: </h3>" + str(item["start"])\
                                       + " " + "<h3>End: </h3>" + str(item["end"]) + "<br><br>"
                    contents = contents + """</u><a href = "http://127.0.0.1:8000/">Click here to return to the main page</a></body></html>"""
            except TypeError:
                status = 400
                # Error page in case the user does not introduce a value or it does not exist.
                with open("error5.html", "r") as file:
                    contents = file.read()


        # This else clause will be used when the user requests a resource that does not exist.

        else:
            status = 400
            name_file = "error.html"
            with open(name_file, "r") as file:
                contents = file.read()


        self.send_response(status)

        # The variable json_send that appears along the practice, is meant to make this two next clauses work.
        # In case the variable equals the boolean value "True", the info asked by the user will be sent in json format.
        # In the opposite case, it will be sent in html format.

        if json_send == True:
            self.send_header("Content-Type", "application/json")  # Send json format in case the user requests it
        else:
            self.send_header('Content-Type', 'text/html')  # Send html format if the user does not want json

        self.send_header('Content-Length', len(str.encode(contents)))

        self.end_headers()

        self.wfile.write(str.encode(contents))

        return

# Main program of the server.

Handler = TestHandler

socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), Handler) as httpd:

    print("Serving at PORT", PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()

print("")
print("Server Stopped")
