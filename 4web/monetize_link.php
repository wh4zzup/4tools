<?php

/************************************************************/
/*                                                          */
/*  Idea/Written by Sebastian Vivian Gresser                */
/*                                                          */
/*  Usage example: include 'monetize_link.php';             */
/*          $mntz = new link_monetizer($config);            */
/*          $mntz->monetize_link('https://www.ebay.com')    */
/*                                                          */
/************************************************************/
/*
/* Example
/************************************************************/
/*
$config = array(
    'ebay'  => array(
        'campid'    => 'yourcampaignid',
        'customid'  => 'yourcustomid'
    ),
    //Amazon Data - please read the affiliate documentations - you need to create a sub array for each market
    'amazon' => array(
                'de' => array(
                    '_encoding' =>  'UTF8',     // needed value string
                    'tag'       =>  'tag_name', // needed value string | e.g. campaign tag name
                    'linkCode'  =>  'ur2',      // mandatory value string | ur2 = textlink
                    //'linkId'    =>  'link_id',
                    'camp'      =>  0,          // needed value integer
                    'creative'  =>  0           // needed value integer
                ),
                'fr' => array(
                    '_encoding' =>  'UTF8',     // needed value string
                    'tag'       =>  'tag_name', // needed value string | e.g. campaign tag name
                    'linkCode'  =>  'ur2',      // mandatory value string | ur2 = textlink
                    //'linkId'    =>  'link_id',
                    'camp'      =>  0,          // needed value integer
                    'creative'  =>  0           // needed value integer
                ),
                //... etc.
    )
);
$mntz = new link_monetizer($config);
print_r($mntz->monetize_link('https://www.ebay.com'));
print_r($mntz->monetize_link('https://www.amazon.de'));

/************************************************************/
/*
Details regarding the linkCode parameter for Amazon links
PRODUCT LINKS:
https://affiliate-program.amazon.com/gp/associates/network/build-links/individual/main.html
-Details Preview-
linkCode=as3
-Details Impression-
linkCode=as2
-Offer Listing Preview-
linkCode=am3
-Offer Listing Impression-
linkCode=am2
-Enhanced Display-
linkCode=as1
linkCode=am1


CONTEXT LINKS
https://affiliate-program.amazon.com/gp/associates/network/build-links/context/main.html
-Context Links Beta-
linkCode=?


OMAKASE LINKS
https://affiliate-program.amazon.com/gp/associates/network/build-links/optimized/main.html
-Omakase Links-
linkCode=op1


RECOMMENDED PRODUCT LINKS
https://affiliate-program.amazon.com/gp/associates/network/build-links/dynamic/main.html
-Category-
linkCode=bn1
-Keyword-
linkCode=st1


BANNER LINKS
https://affiliate-program.amazon.com/gp/associates/network/build-links/banner/main.html
-Category-
linkCode=ur1
-Easy Links-
linkCode=ez
-Homepage Links-
linkCode=?


SEARCH RESULT LINKS
https://affiliate-program.amazon.com/gp/associates/network/build-links/searchbox/main.html
-Basic Search Results-
linkCode=qs1
-Enhanced Search Boxes-
linkCode=qs1


TEXT LINKS
https://affiliate-program.amazon.com/gp/associates/network/build-links/text/main.html
-Link to any page-
linkCode=ur2
-Share on Twitter-
linkCode=?


WEB SERVICE LINKS
http://www.amazon.com/webservices/
-Add-to-cart-
linkCode=?
-REST-
linkCode=xm2
-Remote shopping cart-
linkCode=?
-SOAP-
linkCode=?


ASTORE
https://affiliate-program.amazon.com/gp/associates/network/store/main.html
-Purchase through aStore-
linkCode=?
-Referral from aStore-
linkCode=?

*/

class link_monetizer {
    protected $config;

    public function __construct($config) {
        //eBay Data
        $this->config = $config;
    }

    protected function get_ebay_zone_data($country_code) {
        /* not finished yet since a few zones are not yet complying with the new revenue system */
        $cc = array(    #'us' => array('711-53200-19255-0', 0),
                        'com' => array('711-53200-19255-0', 0),
                        'ie' => array('5282-53468-19255-0', 205),
                        'at' => array('5221-53469-19255-0', 16),
                        #'au' => array('705-53470-19255-0', 15),
                        'com.au' => array('705-53470-19255-0', 15),
                        'be' => array('1553-53471-19255-0', 23),
                        #'in' => array('4686-53472-19255-0', Null),
                        'ca' => array('706-53473-19255-0', 2),
                        #'com.sg' => array('3423-53474-19255-0', Null),
                        #'com.hk' => array('3422-53475-19255-0', Null),
                        'fr' => array('709-53476-19255-0', 71),
                        'de' => array('707-53477-19255-0', 77),
                        'it' => array('724-53478-19255-0', 101),
                        'es' => array('1185-53479-19255-0', 186),
                        'ch' => array('5222-53480-19255-0', 193),
                        #'uk' => array('710-53481-19255-0', 3),
                        'co.uk' => array('710-53481-19255-0', 3),
                        #'cn' => array('4080-53484-19255-0', Null),
                        'nl' => array('1346-53482-19255-0', 146)
        );
        if(isset($cc[$country_code])){
            return $cc[$country_code];
        }
        return false;
    }

    public function monetize_link($link){
        $purl=parse_url($link);
        // eBay
        if(preg_match('/www.?(\w+.|)ebay./', $purl['host'])){
            $country=strtolower(preg_replace('/www.?(\w+.|)ebay./', '', $purl['host']));
            $ps = explode('?', $link);
            if(count($ps) == 1){
                $ps[] = '';
            }
            list($prefix, $param) = $ps;
            parse_str($param, $ps);
            $ps['mkcid']=1;
            $zone_ids = self::get_ebay_zone_data($country);
            if($zone_ids){
                $ps['mkrid']=$zone_ids[0];
                $ps['siteid']=$zone_ids[1];
            }
            $ps['campid']=$this->config['ebay']['campid'];
            $ps['customid']=$this->config['ebay']['customid'];
            $ps['toolid']=10001;
            $ps['mkevt']=1;
            $res = $prefix . '?' . http_build_query($ps);
            return $res;
        }
        // Amazon
        foreach($this->config['amazon'] as $k => $a){
            if(preg_match('/www.amazon.'.$k.'.*/', $purl['host'])){
                $ps = explode('?', $link);
                if(count($ps) == 1){
                    $ps[] = '';
                }
                list($prefix, $param) = $ps;
                parse_str($param, $ps);
                foreach($a as $k_ => $a_){
                    $ps[$k_]=$a_;
                }
                $res = $prefix . '?' . http_build_query($ps);
                return $res;
            }
        }
        return $link;
    }
}


?>
