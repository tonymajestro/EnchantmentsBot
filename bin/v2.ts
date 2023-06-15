#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { EnchantmentsStack } from '../lib/v2-stack';
import * as yaml from 'js-yaml';
import * as fs from 'fs';

interface EnchantmentsConfig {
  sitesTableName: string;
  sitesSnsName: string;
  sitesSubscriptions: string[];
}

const app = new cdk.App();
const config = yaml.load(fs.readFileSync('config/enchantments.yml', 'utf8')) as EnchantmentsConfig;

new EnchantmentsStack(app, 'V2Stack', {
  sitesTableName: config.sitesTableName,
  sitesSnsName: config.sitesSnsName,
  sitesSubscriptions: config.sitesSubscriptions
});