# travis-sidekick

### Posts deploy.txt file as a comment and also removes any old stale comments before posting new. 


* create app and use some dummy url for webook or make one ( I don't have any webserver running )
* get the APP ID and INSTALL ID from github settings and added those to .travis.yml
* encrypt the private key downloaded from the github app. ( - ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `DON'T ADD THE .pem file to github` )

```
#EXAMPLE
[abc@foo travis-sidekick]$ travis encrypt-file travis-sidekick.2020-04-19.private-key.pem -t $TRAVIS_TOKEN --add

```
