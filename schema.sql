-- phpMyAdmin SQL Dump
-- version 3.3.8.1
-- http://www.phpmyadmin.net
--
-- 生成日期: 2014 年 05 月 22 日 08:50
-- 服务器版本: 5.5.27
-- PHP 版本: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

-- --------------------------------------------------------

--
-- 表的结构 `articles`
--

CREATE TABLE IF NOT EXISTS `articles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slug` varchar(200) DEFAULT NULL,
  `title` varchar(200) NOT NULL,
  `seotitle` varchar(200) DEFAULT NULL,
  `seokey` varchar(128) DEFAULT NULL,
  `seodesc` varchar(300) DEFAULT NULL,
  `category_id` int(11) NOT NULL,
  `topic_id` int(11) DEFAULT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `thumbnail_big` varchar(255) DEFAULT NULL,
  `template` varchar(255) DEFAULT NULL,
  `summary` varchar(2000) DEFAULT NULL,
  `body` longtext NOT NULL,
  `body_html` longtext,
  `published` tinyint(1) DEFAULT NULL,
  `ontop` tinyint(1) DEFAULT NULL,
  `recommend` tinyint(1) DEFAULT NULL,
  `hits` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `last_modified` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `topic_id` (`topic_id`),
  KEY `author_id` (`author_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `articles`
--


-- --------------------------------------------------------

--
-- 表的结构 `article_tags`
--

CREATE TABLE IF NOT EXISTS `article_tags` (
  `article_id` int(11) DEFAULT NULL,
  `tag_id` int(11) DEFAULT NULL,
  KEY `article_id` (`article_id`),
  KEY `tag_id` (`tag_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `article_tags`
--


-- --------------------------------------------------------

--
-- 表的结构 `categories`
--

CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slug` varchar(64) NOT NULL,
  `longslug` varchar(255) NOT NULL,
  `name` varchar(64) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `seotitle` varchar(128) DEFAULT NULL,
  `seokey` varchar(128) DEFAULT NULL,
  `seodesc` varchar(300) DEFAULT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `template` varchar(255) DEFAULT NULL,
  `article_template` varchar(255) DEFAULT NULL,
  `body` text,
  `body_html` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_categories_longslug` (`longslug`),
  KEY `parent_id` (`parent_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `categories`
--


-- --------------------------------------------------------

--
-- 表的结构 `flatpages`
--

CREATE TABLE IF NOT EXISTS `flatpages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slug` varchar(32) NOT NULL,
  `title` varchar(100) NOT NULL,
  `seotitle` varchar(200) DEFAULT NULL,
  `seokey` varchar(128) DEFAULT NULL,
  `seodesc` varchar(400) DEFAULT NULL,
  `template` varchar(255) DEFAULT NULL,
  `body` text NOT NULL,
  `body_html` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `flatpages`
--


-- --------------------------------------------------------

--
-- 表的结构 `friendlinks`
--

CREATE TABLE IF NOT EXISTS `friendlinks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `anchor` varchar(64) NOT NULL,
  `title` varchar(128) DEFAULT NULL,
  `url` varchar(255) NOT NULL,
  `actived` tinyint(1) DEFAULT NULL,
  `order` int(11) DEFAULT NULL,
  `note` varchar(400) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `friendlinks`
--


-- --------------------------------------------------------

--
-- 表的结构 `labels`
--

CREATE TABLE IF NOT EXISTS `labels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slug` varchar(32) NOT NULL,
  `title` varchar(100) NOT NULL,
  `html` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `labels`
--


-- --------------------------------------------------------

--
-- 表的结构 `links`
--

CREATE TABLE IF NOT EXISTS `links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `anchor` varchar(64) NOT NULL,
  `title` varchar(128) DEFAULT NULL,
  `url` varchar(255) NOT NULL,
  `note` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `links`
--


-- --------------------------------------------------------

--
-- 表的结构 `redirects`
--

CREATE TABLE IF NOT EXISTS `redirects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `old_path` varchar(128) NOT NULL,
  `new_path` varchar(128) NOT NULL,
  `note` varchar(400) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `redirects`
--


-- --------------------------------------------------------

--
-- 表的结构 `roles`
--

CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `default` tinyint(1) DEFAULT NULL,
  `permissions` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_roles_default` (`default`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4 ;

--
-- 转存表中的数据 `roles`
--

INSERT INTO `roles` (`id`, `name`, `default`, `permissions`) VALUES
(1, 'Moderator', 0, 12),
(2, 'Administrator', 0, 255),
(3, 'User', 1, 4);

-- --------------------------------------------------------

--
-- 表的结构 `tags`
--

CREATE TABLE IF NOT EXISTS `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `seotitle` varchar(128) DEFAULT NULL,
  `seokey` varchar(128) DEFAULT NULL,
  `seodesc` varchar(300) DEFAULT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `template` varchar(255) DEFAULT NULL,
  `body` text,
  `body_html` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_tags_name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `tags`
--


-- --------------------------------------------------------

--
-- 表的结构 `topics`
--

CREATE TABLE IF NOT EXISTS `topics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `slug` varchar(64) NOT NULL,
  `name` varchar(64) NOT NULL,
  `seotitle` varchar(128) DEFAULT NULL,
  `seokey` varchar(128) DEFAULT NULL,
  `seodesc` varchar(300) DEFAULT NULL,
  `thumbnail` varchar(255) DEFAULT NULL,
  `template` varchar(255) DEFAULT NULL,
  `body` text,
  `body_html` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_topics_slug` (`slug`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- 转存表中的数据 `topics`
--


-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `about_me` varchar(1000) DEFAULT NULL,
  `member_since` datetime DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `avatar_hash` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `role_id` (`role_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;


--
-- 表的结构 `settings`
--

CREATE TABLE IF NOT EXISTS `settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `rawvalue` varchar(4096) NOT NULL,
  `formatter` varchar(16) NOT NULL,
  `builtin` tinyint(1) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

