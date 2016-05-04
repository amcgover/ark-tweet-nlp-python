#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Python wrapper for runTagger.sh script for CMU's Tweet Tokeniser and Part of Speech tagger: http://www.ark.cs.cmu.edu/TweetNLP/
Usage:
results=runtagger_parse(['example tweet 1', 'example tweet 2'])
results will contain a list of lists (one per tweet) of triples, each triple represents (term, type, confidence)
"""
import subprocess
import shlex
import re

# The only relavent source I've found is here:
# http://m1ked.com/post/12304626776/pos-tagger-for-twitter-successfully-implemented-in
# which is a very simple implementation, my implementation is a bit more
# useful (but not much).

# NOTE this command is directly lifted from runTagger.sh
RUN_TAGGER_CMD = "java -XX:ParallelGCThreads=2 -Xmx500m -jar ark-tweet-nlp-0.3.2.jar"

def _split_results(rows):
    """Parse the tab-delimited returned lines, modified from: https://github.com/brendano/ark-tweet-nlp/blob/master/scripts/show.py"""
    #rows is a single POS-tagged tweet
    
    for line in rows:
        if len(line) > 0:
            if line.count('\t') == 2:
                parts = line.split('\t')
                tokens = parts[0]
                tags = parts[1]
                confidence = float(parts[2])
                yield tokens, tags, confidence

def _call_runtagger(file_name, run_tagger_cmd=RUN_TAGGER_CMD):
    """Call runTagger.sh using a named input file"""

    # build a list of args
    args = shlex.split(run_tagger_cmd)
    args.append('--output-format')
    args.append('conll')
    args.append(file_name)
    po = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = [l for l in po.stdout]
    
    taggedTweet = [];
    result = [];
    prevLine = '';
    for line in lines:
        if line == '\r\n':
            result.append(taggedTweet);
            taggedTweet = [];
        else:
            taggedTweet.append(line);
   
    return result

def runtagger_parse(tweets, run_tagger_cmd=RUN_TAGGER_CMD):
    """Call runTagger.sh on a list of tweets, parse the result, return lists of tuples of (term, type, confidence)"""
    pos_raw_results = _call_runtagger(tweets, run_tagger_cmd) #Each index contains a fully tagged tweet
    pos_result = []
    for pos_raw_result in pos_raw_results:
        pos_result.append([x for x in _split_results(pos_raw_result)])
    return pos_result

def check_script_is_present(run_tagger_cmd=RUN_TAGGER_CMD):
    """Simple test to make sure we can see the script"""
    success = False
    try:
        args = shlex.split(run_tagger_cmd)
        print args;
        args.append("--help")
        po = subprocess.Popen(args, stdout=subprocess.PIPE)
        # old call - made a direct call to runTagger.sh (not Windows friendly)
        #po = subprocess.Popen([run_tagger_cmd, '--help'], stdout=subprocess.PIPE)
        lines = [l for l in po.stdout]
        
        # we expected the first line of --help to look like the following:
        assert "RunTagger [options]" in lines[0]
        success = True
    except OSError as err:
        print "Caught an OSError, have you specified the correct path to runTagger.sh? We are using \"%s\". Exception: %r" % (run_tagger_cmd, repr(err))
    return success


if __name__ == "__main__":
    print "Checking that we can see \"%s\", this will crash if we can't" % (RUN_TAGGER_CMD)
    success = check_script_is_present()
    if success:
        print "Success."
        print "Now pass in file name, get a list of lists of tuples back:"
        print "Each element in the list is a list of tuples is a POS-tagged tweet."
        print "The first element corresponds to the first line of the file, the second element corresponds to the second line of the file etc."
        tweetFile = 'examples/example_tweets.txt'
        tweetCount = 1;
        for parsedTweet in runtagger_parse(tweetFile):
            print 'Tweet %d\n' % tweetCount;
            for returned_tuple in parsedTweet:
                print returned_tuple;
            tweetCount += 1;
            print '-----------------------------\n';
