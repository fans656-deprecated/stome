import React from 'react'
import $ from 'jquery'
import { withRouter } from 'react-router-dom'

import Console from './Console'
import UserPanel from './UserPanel'
import Nav from './Nav'
import Content from './Content'
import ItemPanel from './ItemPanel'
import StatusBar from './StatusBar'

import vpsUpload from './uploader/vps'
import qiniuUpload from './uploader/qiniu'

import conf from './conf'

import { getTree, Node } from './node'
import { joinPaths, splitBaseName, calcMD5 } from './util'

import './css/Explorer.css'

class Explorer extends React.Component {
  state = {
    tree: null,
    uploadPath: null,
    transfer: null,
  }

  componentWillReceiveProps = async (props) => {
    await this.state.tree.setCurrentPath(props.currentPath);
    this.setState({});
  }

  componentDidMount = async () => {
    window.upload = this.openFileSelection;
    const tree = await getTree(this.props.rootPath, this);
    await tree.setCurrentPath(this.props.currentPath);
    window.root = tree.root;
    this.setState({tree: tree});
  }

  render() {
    const tree = this.state.tree;
    if (!tree) return null;
    return (
      <div className="explorer">
        <header className="horizontal">
          <div className="left child">
            <Console/>
          </div>
          <div className="right child">
            <a
              id="todo"
              href="/?todo"
              target="_blank"
              rel="noopener noreferrer"
            >
              TODO
            </a>
            <UserPanel/>
          </div>
        </header>
        <main className="horizontal">
          <Nav tree={this.state.tree}
            onNodeClicked={this.onNodeClickedInNav}
            onNodeToggled={this.onNodeToggledInNav}
          />
          <Content
            currentDir={this.state.tree.currentDir}
            currentItem={this.state.tree.currentItem}
            onClick={this.onItemClickedInContent}
            onItemChange={() => this.setState({})}
          />
          <ItemPanel node={tree.currentItem || tree.currentDir}/>
        </main>
        <footer>
          <div className="child">
            <StatusBar item={tree.currentItem || tree.currentDir}/>
          </div>
        </footer>
        <div style={{display: 'none'}}>
          <input id="upload"
            type="file"
            multiple
            style={{display: 'none'}}
            onChange={this.onFileInputChange}
          />
        </div>
      </div>
    );
  }

  onNodeClickedInNav = async (node) => {
    if (node.isCurrentDir()) {
      await node.toggle();
    } else {
      this.changeCurrentDir(node);
    }
    this.setState({});
  }

  onItemClickedInContent = async (node) => {
    if (node && node.isCurrentItem()) {
      if (node.meta.listable) {
        this.changeCurrentDir(node);
      } else {
        this.openFile(node);
      }
    } else {
      this.state.tree.currentItem = node;
    }
    this.setState({});
  }

  onNodeToggledInNav = () => {
    this.setState({});
  }

  changeCurrentDir = (node) => {
    this.state.tree.setCurrentDir(node);
    this.props.history.push(node.meta.path);
  }

  openFile = (node) => {
    if (node.transfer) return;
    const url = conf.api_origin + node.meta.path;
    const a = $('<a>');
    a.attr('href', url);
    a.attr('target', '_blank');
    a.attr('rel', 'noopener noreferer');
    a.attr('style', 'display: none');
    $('body').append(a);
    a[0].click();
    a.remove();
  }

  openFileSelection = (path) => {
    this.setState({
      uploadPath: path || '',
    }, () => $('#upload').click());
  }

  onFileInputChange = async () => {
    let [dirpath, name] = splitBaseName(this.state.uploadPath);
    dirpath = joinPaths(this.getCurrentDirPath(), dirpath);
    const fileInput = $('#upload');
    const files = fileInput[0].files;
    if (files.length === 1) {
      this.doUploadFile(dirpath, name, files[0]);
    } else {
      for (let i = 0; i < files.length; ++i) {
        this.doUploadFile(dirpath, null, files[i]);
      }
    }
    fileInput.val(null);
  }

  getCurrentDirPath = () => {
    return this.state.tree.currentDir.meta.path;
  }

  doUploadFile = async (dirpath, name, file) => {
    name = name || file.name;
    const path = joinPaths(dirpath, name);
    const dir = await this.state.tree.findByPath(dirpath);

    const node = makeTransferNode(dir, path, name);
    dir.addFileChild(node);

    const md5 = await calcMD5(file, node.onHashProgress);

    let upload = null;
    if (true) {  // upload to qiniu
      upload = qiniuUpload;
    } else {  // upload to server
      upload = vpsUpload;
    }

    upload({
      path: path,
      dirpath: dirpath,
      name: name,
      md5: md5,
      file: file,
      node: node,
    });
    this.update();
  }

  update = () => {
    this.setState({});
  }
}

function makeTransferNode(dir, path, name) {
  const node = new Node({
    path: path,
    name: name,
    listable: false,
  }, dir, dir.tree);
  node.transfer = {
    status: 'hashing',
  };
  return node;
}

Explorer = withRouter(Explorer);

export default Explorer;
