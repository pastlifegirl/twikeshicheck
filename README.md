# ツイ消しチェッカー
指定したアカウントがツイ消しをしたらその内容をツイートします。

トラブルを避けるため、鍵垢Twitterや身内用Slack、Lineなどで、ジョークとしての運用を推奨します。

# 使い方
.envに設定を書き込み、cronで定期的にcheck.shを実行してください。

cronで設定する場合は、check.shがあるディレクトリまでcdで移動してからのほうが良いでしょう。

データベースを初期化したくなったら、tweets.empty.dbをtweets.dbに上書きしてください。
