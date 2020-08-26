include "rpc/article_thrift.thrift"
struct NLPRequest {
    1:  required article_thrift.ArticleThrift       doc;          // 文章特征
    2:  optional map<string,double>                 classes; //分类
}

struct NLPResp {
    1: required i32 code;
    2: optional string msg;
    3: optional string   title_dssm_vec;                // 标题DSSM向量
    4: optional string   content_dssm_vec;              // 正文DSSM向量
}

service NLPService{
    NLPResp dssm(1:article_thrift.RpcContext ctx, 2:NLPRequest req),
    }
