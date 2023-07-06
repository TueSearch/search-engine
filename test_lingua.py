import tldextract

def extract_domain(url):
    extracted = tldextract.extract(url)
    out = extracted.subdomain + '.' + extracted.domain + '.' + extracted.suffix
    out_tokens = out.split(".")
    if out_tokens[0] == "www":
        return ".".join(out_tokens[1:])
    return out
url = "https://www.webmail.uni-tuebingen.de/imp/dynamic.php?page=mailbox#mbox:SU5CT1g"
domain = extract_domain(url)
print(domain)